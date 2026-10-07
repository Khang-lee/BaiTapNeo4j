import streamlit as st
from neo4j_connection import Neo4jConnection
from geometry_service import GeometryService
from pyvis.network import Network
import streamlit.components.v1 as components
import base64
import html


st.set_page_config(
    page_title="Geometry Knowledge Graph",
    page_icon="📐",
    layout="wide"
)


@st.cache_resource
def get_service():
    db = Neo4jConnection()
    db.verify_connection()
    return GeometryService(db)


def svg_data_uri(svg):
    encoded = base64.b64encode(svg.encode("utf-8")).decode("utf-8")
    return f"data:image/svg+xml;base64,{encoded}"


def create_shape_svg(shape_name):
    if shape_name == "Hình tứ giác":
        polygon = "45,15 155,15 175,85 25,85"
    elif shape_name == "Hình thang":
        polygon = "55,15 145,15 175,85 25,85"
    elif shape_name == "Hình thang cân":
        polygon = "55,15 145,15 170,85 30,85"
    elif shape_name == "Hình thang vuông":
        polygon = "35,15 145,15 170,85 35,85"
    elif shape_name == "Hình bình hành":
        polygon = "55,15 175,15 145,85 25,85"
    elif shape_name == "Hình chữ nhật":
        polygon = "25,20 175,20 175,80 25,80"
    elif shape_name == "Hình thoi":
        polygon = "100,10 175,50 100,90 25,50"
    elif shape_name == "Hình vuông":
        polygon = "40,10 160,10 160,90 40,90"
    else:
        polygon = "25,15 175,15 175,85 25,85"

    svg = f"""
    <svg xmlns="http://www.w3.org/2000/svg" width="220" height="130" viewBox="0 0 220 130">
        <polygon points="{polygon}" fill="#1e293b" stroke="#60a5fa" stroke-width="4" stroke-linejoin="round"/>
        <text x="110" y="120" text-anchor="middle" fill="white" font-size="14" font-family="Arial">{shape_name}</text>
    </svg>
    """
    return svg_data_uri(svg)


def create_graph(service):
    relations = service.get_graph()
    net = Network(height="700px", width="100%", directed=True, bgcolor="#0b1120", font_color="white")
    added_nodes = set()

    for relation in relations:
        from_shape = relation["fromShape"]
        to_shape = relation["toShape"]
        property_added = relation["relation"]

        if not from_shape or not to_shape:
            continue

        if from_shape not in added_nodes:
            net.add_node(from_shape, label="", title=from_shape, shape="image", image=create_shape_svg(from_shape), size=45)
            added_nodes.add(from_shape)

        if to_shape not in added_nodes:
            net.add_node(to_shape, label="", title=to_shape, shape="image", image=create_shape_svg(to_shape), size=45)
            added_nodes.add(to_shape)

        net.add_edge(from_shape, to_shape, label=property_added, title=property_added, arrows="to", color="#94a3b8", font={"color": "white", "size": 12, "strokeWidth": 0})

    net.set_options("""
    {
        "layout": { "hierarchical": { "enabled": true, "direction": "LR", "sortMethod": "directed", "levelSeparation": 250, "nodeSpacing": 180, "treeSpacing": 250 } },
        "physics": { "enabled": false },
        "interaction": { "hover": true, "navigationButtons": true, "keyboard": true, "zoomView": true, "dragView": true },
        "edges": { "smooth": { "type": "cubicBezier", "forceDirection": "horizontal", "roundness": 0.4 }, "arrows": { "to": { "enabled": true, "scaleFactor": 0.8 } }, "font": { "color": "white", "size": 12, "strokeWidth": 0 } }
    }
    """)
    return net


def get_short_property(text, max_sentences=2):
    if not text:
        return ""
    sentences = [s.strip() for s in text.split(".") if s.strip()]
    return ". ".join(sentences[:max_sentences]) + ("." if sentences else "")


def main():
    st.title("📐 Geometry Knowledge Graph")
    st.caption("Mô hình hóa Tứ giác trong hình học phẳng với Neo4j")

    try:
        service = get_service()
    except Exception as e:
        st.error("Không thể kết nối Neo4j.")
        st.code(str(e))
        return

    st.sidebar.header("Chức năng")
    pages = [
        "Danh sách hình", "Chi tiết hình", "Đồ thị Knowledge Graph", 
        "Hình được suy ra", "Tìm đường suy luận", "Tìm kiếm kiến thức", 
        "Máy tính hình học"
    ]

    if "page" not in st.session_state:
        st.session_state["page"] = "Danh sách hình"

    selected_page = st.sidebar.radio("Chọn chức năng", pages, index=pages.index(st.session_state["page"]))
    st.session_state["page"] = selected_page
    option = st.session_state["page"]

    if option == "Danh sách hình":
        st.caption("Tổng quan các loại tứ giác trong Knowledge Graph.")
        shapes = service.get_all_shapes()
        relations = service.get_graph()

        col1, col2, col3 = st.columns(3)
        with col1: st.metric("📐 Loại hình", len(shapes))
        with col2: st.metric("🔗 Quan hệ suy luận", len([x for x in relations if x["relation"]]))
        with col3: st.metric("🧠 Knowledge Graph", "Neo4j")
        st.markdown("---")

        for row_start in range(0, len(shapes), 4):
            cols = st.columns(4)
            for col, shape in zip(cols, shapes[row_start:row_start + 4]):
                with col:
                    name = shape["tenGoi"]
                    image_data = create_shape_svg(name)
                    short_prop = get_short_property(shape["tinhChat"], 2)

                    st.html(f"""
                        <div style="background-color: #151922; border: 1px solid #303642; border-radius: 12px; padding: 16px; min-height: 420px; margin-bottom: 12px;">
                            <div style="text-align: center; margin-bottom: 10px;"><img src="{image_data}" style="width: 190px; height: 120px; object-fit: contain;"></div>
                            <h3 style="text-align: center; color: #ffffff; font-size: 20px;">{html.escape(name)}</h3>
                            <div style="color: #cbd5e1; font-size: 14px; min-height: 75px;"><b style="color:#ffffff;">Tính chất</b><br>{html.escape(short_prop)}</div>
                            <div style="border-top: 1px solid #303642; margin-top: 12px; padding-top: 10px; color: #94a3b8; font-size: 14px;">
                                <div><b style="color:#60a5fa;">Chu vi:</b> {html.escape(shape["chuVi"] or "")}</div>
                                <div style="margin-top:5px;"><b style="color:#60a5fa;">Diện tích:</b> {html.escape(shape["dienTich"] or "")}</div>
                            </div>
                        </div>
                    """)
                    if st.button("Xem chi tiết →", key=f"detail_{row_start}_{name}", use_container_width=True):
                        st.session_state["selected_shape"] = name
                        st.session_state["page"] = "Chi tiết hình"
                        st.rerun()

    elif option == "Chi tiết hình":
        st.header("Thông tin hình")
        shapes = service.get_all_shapes()
        names = [x["tenGoi"] for x in shapes]
        if not names: return

        default_shape = st.session_state.get("selected_shape", names[0])
        selected = st.selectbox("Chọn hình", names, index=names.index(default_shape) if default_shape in names else 0)
        shape = service.get_shape(selected)

        if shape:
            col1, col2 = st.columns([2, 1])
            with col1:
                st.subheader(shape["tenGoi"])
                st.markdown("### Tính chất"); st.write(shape["tinhChat"])
                st.markdown("### Nhận biết"); st.write(shape["nhanBiet"])
                st.markdown("### Chu vi"); st.info(shape["chuVi"])
                st.markdown("### Diện tích"); st.info(shape["dienTich"])
            with col2:
                st.subheader("Hình minh họa")
                st.image(create_shape_svg(shape["tenGoi"]), width=280)

    elif option == "Hình được suy ra":
        st.header("Hình được suy ra từ một hình")
        names = [x["tenGoi"] for x in service.get_all_shapes()]
        selected = st.selectbox("Chọn hình ban đầu", names)
        results = service.get_derived_shapes(selected)
        if results:
            for item in results: st.success(f"{selected} + {item['tinhChatThem']} → **{item['tenGoi']}**")
        else: st.info("Không có hình được suy ra trực tiếp.")

    elif option == "Tìm đường suy luận":
        st.header("Tìm đường suy luận trong Knowledge Graph")
        names = [x["tenGoi"] for x in service.get_all_shapes()]
        col1, col2 = st.columns(2)
        with col1: start = st.selectbox("Hình bắt đầu", names, index=0)
        with col2: end = st.selectbox("Hình cần tìm", names, index=names.index("Hình vuông") if "Hình vuông" in names else 0)

        if st.button("🔎 Tìm đường"):
            paths = service.find_paths(start, end)
            if paths:
                for i, res in enumerate(paths, start=1):
                    st.markdown(f"### Đường {i}")
                    st.write(" → ".join(res["path"]))
            else: st.warning("Không tìm thấy đường.")

    elif option == "Tìm kiếm kiến thức":
        st.header("Tìm kiếm kiến thức hình học")
        keyword = st.text_input("Nhập từ khóa", placeholder="Ví dụ: vuông, song song...")
        if keyword:
            results = service.search_shapes(keyword)
            if results:
                for item in results:
                    with st.expander(item["tenGoi"]):
                        st.markdown("**Tính chất:**"); st.write(item["tinhChat"])
            else: st.warning("Không tìm thấy kết quả.")

    elif option == "Máy tính hình học":
        st.header("🧮 Máy tính hình học & Mô phỏng tỷ lệ thực tế")
        st.write("Dùng thanh trượt để thay đổi thông số; hình vẽ SVG bên phải sẽ co giãn và thay đổi kích thước theo đúng tỷ lệ thực tế.")
        
        shape_choice = st.selectbox(
            "Chọn loại hình muốn tính toán", 
            [
                "Hình chữ nhật", 
                "Hình vuông", 
                "Hình bình hành", 
                "Hình thoi", 
                "Hình thang", 
                "Hình thang cân", 
                "Hình thang vuông", 
                "Hình tứ giác"
            ]
        )

        col1, col2 = st.columns([1, 1])
        svg_content = ""

        with col1:
            if shape_choice == "Hình chữ nhật":
                dai = st.slider("Chiều dài (a):", 2.0, 20.0, 10.0, 0.5)
                rong = st.slider("Chiều rộng (b):", 2.0, 20.0, 6.0, 0.5)
                chu_vi = (dai + rong) * 2
                dien_tich = dai * rong
                st.success(f"**Chu vi:** ({dai} + {rong}) × 2 = {chu_vi}")
                st.success(f"**Diện tích:** {dai} × {rong} = {dien_tich}")

                scale_w = 160 / max(dai, rong)
                scale_h = 110 / max(dai, rong)
                w_px = dai * scale_w
                h_px = rong * scale_h
                x0 = (260 - w_px) / 2
                y0 = (140 - h_px) / 2

                svg_content = f"""
                <svg xmlns="http://www.w3.org/2000/svg" width="260" height="160" viewBox="0 0 260 160" style="background: #151922; border-radius: 8px; padding: 10px;">
                    <rect x="{x0}" y="{y0}" width="{w_px}" height="{h_px}" fill="#1e293b" stroke="#60a5fa" stroke-width="3"/>
                    <line x1="{x0}" y1="{y0}" x2="{x0 + w_px}" y2="{y0 + h_px}" stroke="#f43f5e" stroke-width="2" stroke-dasharray="5,5"/>
                    <text x="130" y="20" fill="white" font-size="12" text-anchor="middle">Dài: {dai} | Rộng: {rong}</text>
                </svg>"""

            elif shape_choice == "Hình vuông":
                canh = st.slider("Cạnh (a):", 2.0, 20.0, 8.0, 0.5)
                chu_vi = canh * 4
                dien_tich = canh * canh
                st.success(f"**Chu vi:** {canh} × 4 = {chu_vi}")
                st.success(f"**Diện tích:** {canh} × {canh} = {dien_tich}")

                scale = 110 / max(canh, 1)
                size_px = canh * scale
                x0 = (260 - size_px) / 2
                y0 = (140 - size_px) / 2

                svg_content = f"""
                <svg xmlns="http://www.w3.org/2000/svg" width="260" height="160" viewBox="0 0 260 160" style="background: #151922; border-radius: 8px; padding: 10px;">
                    <rect x="{x0}" y="{y0}" width="{size_px}" height="{size_px}" fill="#1e293b" stroke="#60a5fa" stroke-width="3"/>
                    <line x1="{x0}" y1="{y0}" x2="{x0 + size_px}" y2="{y0 + size_px}" stroke="#f43f5e" stroke-width="2" stroke-dasharray="5,5"/>
                    <text x="130" y="20" fill="white" font-size="12" text-anchor="middle">Cạnh: {canh}</text>
                </svg>"""

            elif shape_choice == "Hình bình hành":
                day = st.slider("Cạnh đáy (a):", 2.0, 20.0, 10.0, 0.5)
                chieu_cao = st.slider("Chiều cao (h):", 1.0, 15.0, 6.0, 0.5)
                dien_tich = day * chieu_cao
                st.success(f"**Diện tích:** {day} × {chieu_cao} = {dien_tich}")

                scale = 110 / max(day, chieu_cao, 1)
                w_px = day * scale
                h_px = chieu_cao * scale
                offset_x = h_px * 0.6
                
                x_start = (260 - (w_px + offset_x)) / 2
                y_start = (140 - h_px) / 2 + 10

                p1_x, p1_y = x_start + offset_x, y_start
                p2_x, p2_y = x_start + offset_x + w_px, y_start
                p3_x, p3_y = x_start + w_px, y_start + h_px
                p4_x, p4_y = x_start, y_start + h_px

                svg_content = f"""
                <svg xmlns="http://www.w3.org/2000/svg" width="260" height="160" viewBox="0 0 260 160" style="background: #151922; border-radius: 8px; padding: 10px;">
                    <polygon points="{p1_x},{p1_y} {p2_x},{p2_y} {p3_x},{p3_y} {p4_x},{p4_y}" fill="#1e293b" stroke="#60a5fa" stroke-width="3"/>
                    <line x1="{p1_x}" y1="{p1_y}" x2="{p1_x}" y2="{p4_y}" stroke="#f43f5e" stroke-width="2" stroke-dasharray="5,5"/>
                    <text x="130" y="20" fill="white" font-size="12" text-anchor="middle">Đáy: {day} | Cao: {chieu_cao}</text>
                </svg>"""

            elif shape_choice == "Hình thoi":
                d1 = st.slider("Đường chéo 1 (d1):", 2.0, 20.0, 10.0, 0.5)
                d2 = st.slider("Đường chéo 2 (d2):", 2.0, 20.0, 8.0, 0.5)
                dien_tich = 0.5 * d1 * d2
                st.success(f"**Diện tích:** 0.5 × {d1} × {d2} = {dien_tich}")

                scale = 110 / max(d1, d2, 1)
                w_px = d1 * scale
                h_px = d2 * scale
                cx, cy = 130, 80

                p1_x, p1_y = cx, cy - h_px / 2
                p2_x, p2_y = cx + w_px / 2, cy
                p3_x, p3_y = cx, cy + h_px / 2
                p4_x, p4_y = cx - w_px / 2, cy

                svg_content = f"""
                <svg xmlns="http://www.w3.org/2000/svg" width="260" height="160" viewBox="0 0 260 160" style="background: #151922; border-radius: 8px; padding: 10px;">
                    <polygon points="{p1_x},{p1_y} {p2_x},{p2_y} {p3_x},{p3_y} {p4_x},{p4_y}" fill="#1e293b" stroke="#60a5fa" stroke-width="3"/>
                    <line x1="{p4_x}" y1="{p4_y}" x2="{p2_x}" y2="{p2_y}" stroke="#f43f5e" stroke-width="2" stroke-dasharray="5,5"/>
                    <text x="130" y="20" fill="white" font-size="11" text-anchor="middle">d1: {d1} | d2: {d2}</text>
                </svg>"""

            else:
                st.info(f"Đang hiển thị mô phỏng tỷ lệ cho hình: {shape_choice}")
                svg_content = f"""<svg xmlns="http://www.w3.org/2000/svg" width="260" height="160" viewBox="0 0 260 160" style="background: #151922; border-radius: 8px; padding: 10px;"><polygon points="40,30 220,40 190,130 30,100" fill="#1e293b" stroke="#60a5fa" stroke-width="3"/><text x="130" y="20" fill="white" font-size="12" text-anchor="middle">{shape_choice}</text></svg>"""

        with col2:
            st.markdown("### 🖼 Mô hình trực quan tỷ lệ thực tế:")
            if svg_content:
                st.components.v1.html(svg_content, height=180)

    elif option == "Đồ thị Knowledge Graph":
        st.header("🕸️ Knowledge Graph - Tứ giác")
        components.html(create_graph(service).generate_html(), height=700, scrolling=True)


if __name__ == "__main__":
    main()