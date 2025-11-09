import streamlit as st
import pandas as pd
import networkx as nx
from bank_optimizer import BankCoverageOptimizer, optimize_province
from PIL import Image
import plotly.graph_objects as go
import matplotlib.pyplot as plt
import contextily as cx

# --- Page config ---
icon = Image.open("assets/logo_small.png")
st.set_page_config(
    page_title="AI'll find it — Generació De Graf i Proposta",
    page_icon=icon,
    layout="wide"
)

st.title("Bank Coverage Optimizer")
st.markdown("Upload your dataset to create a graph and find optimal office locations.")

# --- File upload ---
uploaded_file = st.file_uploader("📂 Upload CSV or Excel file", type=["csv", "xlsx"])

if uploaded_file:
    if uploaded_file.name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)

    st.subheader("Preview of uploaded data")
    st.dataframe(df.head())

    required_cols = {'name', 'utm_x', 'utm_y', 'pop_0_14', 'pop_15_64', 'pop_65_plus'}
    if not required_cols.issubset(df.columns):
        st.error(f"The file must contain the following columns: {', '.join(required_cols)}")
        st.stop()

    # --- Parameters ---
    st.header("Parameters")
    num_offices = st.number_input("Number of physical offices", min_value=1, value=3)
    num_vans = st.number_input("Number of mobile van stops", min_value=1, value=5)
    office_radius = st.number_input("Physical office radius (m)", min_value=1000, value=15000)
    van_radius = st.number_input("Mobile van radius (m)", min_value=1000, value=10000)
    connection_distance = st.number_input("Distance threshold to connect towns (m)", min_value=1000, value=20000)

    if st.button("🚀 Run Optimization"):
        st.info("Creating graph and computing distances...")

        G = nx.Graph()
        for _, row in df.iterrows():
            G.add_node(
                row['name'],
                name=row['name'],
                utm_x=row['utm_x'],
                utm_y=row['utm_y'],
                pop_0_14=row['pop_0_14'],
                pop_15_64=row['pop_15_64'],
                pop_65_plus=row['pop_65_plus']
            )

        nodes = list(G.nodes)
        for i, node1 in enumerate(nodes):
            for j in range(i + 1, len(nodes)):
                node2 = nodes[j]
                x1, y1 = G.nodes[node1]['utm_x'], G.nodes[node1]['utm_y']
                x2, y2 = G.nodes[node2]['utm_x'], G.nodes[node2]['utm_y']
                dist = ((x1 - x2)**2 + (y1 - y2)**2)**0.5
                if dist <= connection_distance:
                    G.add_edge(node1, node2, weight=dist)

        st.success(f"✅ Graph created with {G.number_of_nodes()} nodes and {G.number_of_edges()} edges.")

        # --- Run optimization ---
        optimizer = BankCoverageOptimizer(G, physical_office_radius=office_radius, mobile_van_radius=van_radius)
        results = optimizer.optimize_coverage(num_offices, num_vans)
        summary = optimizer.get_coverage_summary()

        # --- Show results ---
        st.subheader("📊 Optimization Results")
        st.write(results)

        st.subheader("🏘️ Coverage Summary")
        st.dataframe(summary)

        csv = summary.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="💾 Download coverage summary CSV",
            data=csv,
            file_name="coverage_summary.csv",
            mime="text/csv"
        )

        # --- Plot coverage map (matplotlib + contextily) ---
        st.subheader("🗺️ Coverage Map")
        def visualize_graph_on_map(G, title="Graph on Map", crs_epsg=25831):
            fig, ax = plt.subplots(figsize=(12, 10))
            pos = {node: (data['utm_x'], data['utm_y']) for node, data in G.nodes(data=True)}

            # Draw edges
            nx.draw_networkx_edges(G, pos, ax=ax, edge_color='gray', alpha=0.5)

            # Draw nodes by type
            node_types = {'physical_office': 'blue', 'mobile_van_stop': 'purple', 'uncovered': 'red'}
            for ntype, color in node_types.items():
                nodes_of_type = [n for n, d in G.nodes(data=True) if d.get('node_type', 'uncovered') == ntype]
                nx.draw_networkx_nodes(G, pos, nodelist=nodes_of_type, node_color=color, node_size=100, label=ntype)

            # Labels
            labels = {n: d.get('name','') for n, d in G.nodes(data=True)}
            nx.draw_networkx_labels(G, pos, labels=labels, font_size=8)

            xs = [p[0] for p in pos.values()]
            ys = [p[1] for p in pos.values()]
            buffer_x, buffer_y = (max(xs) - min(xs)) * 0.05, (max(ys) - min(ys)) * 0.05
            ax.set_xlim(min(xs)-buffer_x, max(xs)+buffer_x)
            ax.set_ylim(min(ys)-buffer_y, max(ys)+buffer_y)

            cx.add_basemap(ax, crs=f'epsg:{crs_epsg}', source=cx.providers.CartoDB.Positron)

            ax.set_title(title, fontsize=16)
            ax.set_xlabel('UTM X')
            ax.set_ylabel('UTM Y')
            ax.set_aspect('equal')
            plt.legend()
            st.pyplot(fig)

        visualize_graph_on_map(G, title="Optimized Graph on Map")

        # --- Optional: Plot interactive graph with Plotly ---
        st.subheader("🗺️ Interactive Graph Visualization")
        pos = {node: (G.nodes[node]['utm_x'], G.nodes[node]['utm_y']) for node in G.nodes}
        office_nodes = set(results.get('physical_offices', []))
        van_nodes = set(results.get('mobile_stops', []))  # corrected key

        edge_x, edge_y = [], []
        for edge in G.edges():
            x0, y0 = pos[edge[0]]
            x1, y1 = pos[edge[1]]
            edge_x.extend([x0, x1, None])
            edge_y.extend([y0, y1, None])
        edge_trace = go.Scatter(x=edge_x, y=edge_y, line=dict(width=0.5,color='#888'), hoverinfo='none', mode='lines')

        node_x, node_y, node_color, node_text = [], [], [], []
        for node in G.nodes():
            x, y = pos[node]
            node_x.append(x)
            node_y.append(y)
            if node in office_nodes:
                node_color.append("red")
                node_text.append(f"{node} 🏢 (Office)")
            elif node in van_nodes:
                node_color.append("orange")
                node_text.append(f"{node} 🚐 (Mobile Van)")
            else:
                node_color.append("lightblue")
                node_text.append(node)

        node_trace = go.Scatter(x=node_x, y=node_y, mode='markers', hoverinfo='text',
                                marker=dict(showscale=False, color=node_color, size=10, line_width=1),
                                text=node_text)

        fig = go.Figure(data=[edge_trace, node_trace],
                        layout=go.Layout(title=dict(text='Optimized Graph Visualization', font=dict(size=18)),
                                         showlegend=False, hovermode='closest',
                                         margin=dict(b=20,l=5,r=5,t=40),
                                         xaxis=dict(showgrid=False, zeroline=False),
                                         yaxis=dict(showgrid=False, zeroline=False)))
        st.plotly_chart(fig, use_container_width=True)