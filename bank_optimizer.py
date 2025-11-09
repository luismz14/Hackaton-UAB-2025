import networkx as nx
import numpy as np
import pandas as pd
from collections import defaultdict
import matplotlib.pyplot as plt
import contextily as cx

class BankCoverageOptimizer:
    """
    Optimizes the placement of physical bank offices and mobile van stops
    to maximize population coverage in rural areas.
    """

    def __init__(self, graph, physical_office_radius=15000, mobile_van_radius=10000):
        """
        Initialize the optimizer.

        Parameters:
        - graph: NetworkX graph with nodes containing population and coordinates
        - physical_office_radius: Coverage radius for physical offices (meters)
        - mobile_van_radius: Coverage radius for mobile van stops (meters)
        """
        self.G = graph
        self.physical_office_radius = physical_office_radius
        self.mobile_van_radius = mobile_van_radius

        # Initialize all nodes as uncovered
        for node in self.G.nodes():
            self.G.nodes[node]['node_type'] = 'uncovered'
            self.G.nodes[node]['covered_by'] = []
            self.G.nodes[node]['coverage_score'] = 0

    def get_total_population(self, node):
        """Get total population of a node across all age groups."""
        data = self.G.nodes[node]
        pop_0_14 = data.get('pop_0_14', 0)
        pop_15_64 = data.get('pop_15_64', 0)
        pop_65_plus = data.get('pop_65_plus', 0)
        return pop_0_14 + pop_15_64 + pop_65_plus

    def calculate_distance(self, node1, node2):
        """Calculate Euclidean distance between two nodes."""
        data1 = self.G.nodes[node1]
        data2 = self.G.nodes[node2]

        x1, y1 = data1['utm_x'], data1['utm_y']
        x2, y2 = data2['utm_x'], data2['utm_y']

        return np.sqrt((x1 - x2)**2 + (y1 - y2)**2)

    def get_nodes_within_radius(self, center_node, radius):
        """Get all nodes within a given radius of the center node."""
        nodes_in_radius = []

        for node in self.G.nodes():
            if node == center_node:
                nodes_in_radius.append(node)
            else:
                distance = self.calculate_distance(center_node, node)
                if distance <= radius:
                    nodes_in_radius.append(node)

        return nodes_in_radius

    def calculate_coverage_score(self, node, radius, already_covered=None):
        """
        Calculate coverage score for a potential facility location.
        Score = weighted sum of uncovered population within radius.
        Closer nodes get higher weight.
        """
        if already_covered is None:
            already_covered = set()

        nodes_in_radius = self.get_nodes_within_radius(node, radius)
        total_score = 0

        for nearby_node in nodes_in_radius:
            if nearby_node in already_covered:
                continue

            population = self.get_total_population(nearby_node)
            distance = self.calculate_distance(node, nearby_node) if node != nearby_node else 1

            # Weight by inverse distance (closer = more valuable)
            # Add 1 to avoid division by zero
            weight = 1 / (distance / 1000 + 1)  # Convert to km

            total_score += population * weight

        return total_score

    def select_physical_offices(self, num_offices):
        """
        Select optimal locations for physical bank offices using greedy algorithm.

        Returns: List of node IDs for physical office locations
        """
        print(f"\n{'='*60}")
        print(f"SELECTING {num_offices} PHYSICAL OFFICE LOCATIONS")
        print(f"{'='*60}")

        selected_offices = []
        covered_nodes = set()

        for iteration in range(num_offices):
            best_node = None
            best_score = -1
            best_coverage = []

            # Evaluate each uncovered node
            for node in self.G.nodes():
                if node in selected_offices:
                    continue

                score = self.calculate_coverage_score(
                    node,
                    self.physical_office_radius,
                    covered_nodes
                )

                if score > best_score:
                    best_score = score
                    best_node = node
                    best_coverage = self.get_nodes_within_radius(
                        node,
                        self.physical_office_radius
                    )

            if best_node is None:
                print(f"  ⚠ No more beneficial locations found after {iteration} offices")
                break

            # Add the best location
            selected_offices.append(best_node)

            # Mark nodes as covered
            newly_covered = 0
            newly_covered_pop = 0
            for covered_node in best_coverage:
                if covered_node not in covered_nodes:
                    newly_covered += 1
                    newly_covered_pop += self.get_total_population(covered_node)
                covered_nodes.add(covered_node)
                self.G.nodes[covered_node]['covered_by'].append(best_node)

            # Update node type
            self.G.nodes[best_node]['node_type'] = 'physical_office'
            self.G.nodes[best_node]['coverage_score'] = best_score

            node_name = self.G.nodes[best_node].get('name', f'Node {best_node}')
            node_pop = self.get_total_population(best_node)

            print(f"\n  Office {iteration + 1}: {node_name} (Code: {best_node})")
            print(f"    Population: {node_pop:,}")
            print(f"    Coverage Score: {best_score:,.0f}")
            print(f"    Newly Covered Cities: {newly_covered}")
            print(f"    Newly Covered Population: {newly_covered_pop:,}")
            print(f"    Total Cities Covered: {len(covered_nodes)}")

        return selected_offices, covered_nodes

    def select_mobile_van_stops(self, num_stops, exclude_nodes=None):
        """
        Select optimal locations for mobile van stops.
        Focuses on areas not covered by physical offices.

        Returns: List of node IDs for mobile van stop locations
        """
        print(f"\n{'='*60}")
        print(f"SELECTING {num_stops} MOBILE VAN STOP LOCATIONS")
        print(f"{'='*60}")

        if exclude_nodes is None:
            exclude_nodes = set()

        selected_stops = []
        covered_nodes = exclude_nodes.copy()

        for iteration in range(num_stops):
            best_node = None
            best_score = -1
            best_coverage = []

            # Evaluate each node not yet covered
            for node in self.G.nodes():
                if node in selected_stops or node in exclude_nodes:
                    continue

                score = self.calculate_coverage_score(
                    node,
                    self.mobile_van_radius,
                    covered_nodes
                )

                if score > best_score:
                    best_score = score
                    best_node = node
                    best_coverage = self.get_nodes_within_radius(
                        node,
                        self.mobile_van_radius
                    )

            if best_node is None:
                print(f"  ⚠ No more beneficial locations found after {iteration} stops")
                break

            # Add the best location
            selected_stops.append(best_node)

            # Mark nodes as covered
            newly_covered = 0
            newly_covered_pop = 0
            for covered_node in best_coverage:
                if covered_node not in covered_nodes:
                    newly_covered += 1
                    newly_covered_pop += self.get_total_population(covered_node)
                covered_nodes.add(covered_node)
                self.G.nodes[covered_node]['covered_by'].append(best_node)

            # Update node type
            if self.G.nodes[best_node]['node_type'] == 'uncovered':
                self.G.nodes[best_node]['node_type'] = 'mobile_van_stop'
            self.G.nodes[best_node]['coverage_score'] = best_score

            node_name = self.G.nodes[best_node].get('name', f'Node {best_node}')
            node_pop = self.get_total_population(best_node)

            print(f"\n  Van Stop {iteration + 1}: {node_name} (Code: {best_node})")
            print(f"    Population: {node_pop:,}")
            print(f"    Coverage Score: {best_score:,.0f}")
            print(f"    Newly Covered Cities: {newly_covered}")
            print(f"    Newly Covered Population: {newly_covered_pop:,}")
            print(f"    Total Cities Covered: {len(covered_nodes)}")

        return selected_stops, covered_nodes

    def optimize_coverage(self, num_physical_offices, num_mobile_stops):
        """
        Complete optimization: select both physical offices and mobile van stops.

        Returns: Dictionary with results
        """
        print(f"\n{'#'*60}")
        print(f"# BANK COVERAGE OPTIMIZATION")
        print(f"# Physical Offices: {num_physical_offices}")
        print(f"# Mobile Van Stops: {num_mobile_stops}")
        print(f"{'#'*60}")

        # Step 1: Select physical offices
        physical_offices, covered_by_offices = self.select_physical_offices(num_physical_offices)

        # Step 2: Select mobile van stops for remaining areas
        mobile_stops, all_covered = self.select_mobile_van_stops(
            num_mobile_stops,
            exclude_nodes=covered_by_offices
        )

        # Calculate final statistics
        total_nodes = self.G.number_of_nodes()
        total_population = sum(self.get_total_population(node) for node in self.G.nodes())
        covered_population = sum(
            self.get_total_population(node)
            for node in all_covered
        )

        coverage_rate = (len(all_covered) / total_nodes) * 100
        population_coverage_rate = (covered_population / total_population) * 100

        print(f"\n{'='*60}")
        print(f"FINAL COVERAGE RESULTS")
        print(f"{'='*60}")
        print(f"  Total Municipalities: {total_nodes}")
        print(f"  Covered Municipalities: {len(all_covered)}")
        print(f"  Coverage Rate: {coverage_rate:.2f}%")
        print(f"  ")
        print(f"  Total Population: {total_population:,}")
        print(f"  Covered Population: {covered_population:,}")
        print(f"  Population Coverage Rate: {population_coverage_rate:.2f}%")
        print(f"  ")
        print(f"  Physical Offices: {len(physical_offices)}")
        print(f"  Mobile Van Stops: {len(mobile_stops)}")
        print(f"{'='*60}\n")

        return {
            'physical_offices': physical_offices,
            'mobile_stops': mobile_stops,
            'covered_nodes': all_covered,
            'total_nodes': total_nodes,
            'coverage_rate': coverage_rate,
            'total_population': total_population,
            'covered_population': covered_population,
            'population_coverage_rate': population_coverage_rate
        }

    def get_coverage_summary(self):
        """Get a summary DataFrame of all nodes with their coverage status."""
        data = []

        for node in self.G.nodes():
            node_data = self.G.nodes[node]
            total_pop = self.get_total_population(node)

            data.append({
                'code': node,
                'name': node_data.get('name', 'Unknown'),
                'node_type': node_data.get('node_type', 'uncovered'),
                'population': total_pop,
                'coverage_score': node_data.get('coverage_score', 0),
                'covered_by_count': len(node_data.get('covered_by', [])),
                'utm_x': node_data['utm_x'],
                'utm_y': node_data['utm_y']
            })

        df = pd.DataFrame(data)
        return df.sort_values('population', ascending=False)

    def visualize_coverage(self, title="Bank Coverage Map", figsize=(15, 12), show_map_background=False):
        """
        Visualize the coverage with different colors for each node type.
        - Green (lightgreen): Nodes covered by a physical office or mobile van stop (within radius).
        - Yellow: Nodes NOT covered by a facility, but connected by an edge to a GREEN (lightgreen) node.
        - Red: Truly uncovered nodes.
        - Blue: Physical Offices (these are also green, but drawn on top with a distinct shape).
        - Purple: Mobile Van Stops (these are also green, but drawn on top with a distinct shape).
        """
        fig, ax = plt.subplots(figsize=figsize)

        pos = {node: (self.G.nodes[node]['utm_x'], self.G.nodes[node]['utm_y'])
               for node in self.G.nodes()}

        # 1. Identify Green (lightgreen) nodes (covered by a facility's radius)
        green_nodes_set = {n for n in self.G.nodes() if len(self.G.nodes[n]['covered_by']) > 0}
        green_nodes = list(green_nodes_set)

        # 2. Identify Yellow nodes (adjacent to green, but not green themselves)
        yellow_nodes_set = set()
        for node in self.G.nodes():
            if node not in green_nodes_set: # Only consider nodes not already covered (green)
                for neighbor in self.G.neighbors(node):
                    if neighbor in green_nodes_set:
                        yellow_nodes_set.add(node)
                        break # Found a green neighbor, move to next node

        yellow_nodes = list(yellow_nodes_set)


        # 3. Identify Red nodes (truly uncovered)
        red_nodes = [n for n in self.G.nodes()
                     if n not in green_nodes_set and n not in yellow_nodes_set]

        # 4. Identify Physical Offices and Mobile Van Stops (these are a subset of green_nodes)
        physical_offices = [n for n in self.G.nodes()
                            if self.G.nodes[n]['node_type'] == 'physical_office']
        mobile_stops = [n for n in self.G.nodes()
                        if self.G.nodes[n]['node_type'] == 'mobile_van_stop']


        # Draw edges first (in background)
        nx.draw_networkx_edges(self.G, pos, ax=ax, alpha=0.2, width=0.5, edge_color='gray')

        # Draw nodes by type, starting from the "least covered" to "most covered"
        # This ensures facilities are drawn on top for visibility if they share a coordinate

        if red_nodes:
            nx.draw_networkx_nodes(self.G, pos, nodelist=red_nodes, ax=ax,
                                  node_color='red', node_size=30,
                                  alpha=0.6, label='Truly Uncovered')

        if yellow_nodes:
            nx.draw_networkx_nodes(self.G, pos, nodelist=yellow_nodes, ax=ax,
                                  node_color='yellow', node_size=40,
                                  alpha=0.7, label='Adjacent to Covered')

        if green_nodes: # These include physical offices and mobile stops
            # Draw green nodes that are NOT facilities, or just draw all green nodes as background
            # If a node is a physical office or mobile stop, it will be redrawn later
            non_facility_green_nodes = [n for n in green_nodes if n not in physical_offices and n not in mobile_stops]
            nx.draw_networkx_nodes(self.G, pos, nodelist=non_facility_green_nodes, ax=ax,
                                  node_color='lightgreen', node_size=50,
                                  alpha=0.8, label='Covered by Facility')


        # Draw facilities on top with distinct colors and shapes
        if mobile_stops:
            nx.draw_networkx_nodes(self.G, pos, nodelist=mobile_stops, ax=ax,
                                  node_color='purple', node_size=200,
                                  alpha=0.9, label='Mobile Van Stop',
                                  node_shape='s')

        if physical_offices:
            nx.draw_networkx_nodes(self.G, pos, nodelist=physical_offices, ax=ax,
                                  node_color='blue', node_size=300,
                                  alpha=0.9, label='Physical Office',
                                  node_shape='D')

        # Add labels for facilities
        facility_labels = {n: self.G.nodes[n].get('name', '')
                          for n in mobile_stops + physical_offices}
        nx.draw_networkx_labels(self.G, pos, labels=facility_labels, ax=ax,
                               font_size=8, font_weight='bold')

        if show_map_background:
            # Get bounding box for the basemap
            all_x = [p[0] for p in pos.values()]
            all_y = [p[1] for p in pos.values()]
            min_x, max_x = min(all_x), max(all_x)
            min_y, max_y = min(all_y), max(all_y)

            # Add a small buffer to the limits for better visualization
            buffer_x = (max_x - min_x) * 0.05
            buffer_y = (max_y - min_y) * 0.05
            ax.set_xlim(min_x - buffer_x, max_x + buffer_x)
            ax.set_ylim(min_y - buffer_y, max_y + buffer_y)

            # Add basemap with appropriate CRS (e.g., EPSG:25831 for UTM zone 31N in Spain)
            cx.add_basemap(ax, crs='epsg:25831', source=cx.providers.CartoDB.Positron)
            ax.set_xlabel('UTM X (meters)', fontsize=12)
            ax.set_ylabel('UTM Y (meters)', fontsize=12)
        else:
            ax.set_xlabel('UTM X (meters)', fontsize=12)
            ax.set_ylabel('UTM Y (meters)', fontsize=12)

        ax.set_aspect('equal') # Ensure correct aspect ratio for maps
        plt.title(title, fontsize=16, fontweight='bold')
        plt.legend(scatterpoints=1, loc='best', fontsize=12)
        plt.tight_layout()
        plt.savefig(f'{title.replace(" ", "_").lower()}.png', dpi=150, bbox_inches='tight')
        plt.show()


# ===== USAGE EXAMPLE =====

def optimize_province(graph, province_name, num_offices=3, num_van_stops=5, show_map_background=False):
    """
    Optimize coverage for a province graph.

    Parameters:
    - graph: NetworkX graph
    - province_name: Name of the province (for display)
    - num_offices: Number of physical offices to place
    - num_van_stops: Number of mobile van stops to place
    - show_map_background: Boolean, whether to show map tiles as background
    """
    print(f"\n\n{'#'*70}")
    print(f"# OPTIMIZING COVERAGE FOR {province_name.upper()}")
    print(f"{'#'*70}\n")

    optimizer = BankCoverageOptimizer(
        graph,
        physical_office_radius=15000,  # 15 km
        mobile_van_radius=15000         # 15 km (changed from 10km to match edge distance)
    )

    results = optimizer.optimize_coverage(num_offices, num_van_stops)

    # Get summary
    summary_df = optimizer.get_coverage_summary()

    # Display top facilities
    print("\n" + "="*60)
    print("PHYSICAL OFFICE LOCATIONS:")
    print("="*60)
    offices_df = summary_df[summary_df['node_type'] == 'physical_office']
    print(offices_df[['code', 'name', 'population', 'coverage_score']].to_string(index=False))

    print("\n" + "="*60)
    print("MOBILE VAN STOP LOCATIONS:")
    print("="*60)
    vans_df = summary_df[summary_df['node_type'] == 'mobile_van_stop']
    print(vans_df[['code', 'name', 'population', 'coverage_score']].to_string(index=False))

    # Visualize
    optimizer.visualize_coverage(title=f"{province_name} Bank Coverage", show_map_background=show_map_background)

    return optimizer, results, summary_df


# ===== APPLY TO YOUR GRAPHS =====
"""
# Example usage with your graphs:

# For Lleida
optimizer_lleida, results_lleida, summary_lleida = optimize_province(
    G_lleida,
    "Lleida",
    num_offices=2,
    num_van_stops=4
)

# For Girona
optimizer_girona, results_girona, summary_girona = optimize_province(
    G_girona,
    "Girona",
    num_offices=3,
    num_van_stops=5
)

# For Tarragona
optimizer_tarragona, results_tarragona, summary_tarragona = optimize_province(
    G_tarragona,
    "Tarragona",
    num_offices=2,
    num_van_stops=4
)

# Save the modified graphs
nx.write_graphml(G_lleida, 'lleida_optimized.graphml')
nx.write_graphml(G_girona, 'girona_optimized.graphml')
nx.write_graphml(G_tarragona, 'tarragona_optimized.graphml')

# Export summary to CSV
summary_lleida.to_csv('lleida_coverage_summary.csv', index=False)
summary_girona.to_csv('girona_coverage_summary.csv', index=False)
summary_tarragona.to_csv('tarragona_coverage_summary.csv', index=False)
"""