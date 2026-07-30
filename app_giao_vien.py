import streamlit as st
import pandas as pd
import datetime
import os

# --- CẤU HÌNH KẾT NỐI SUPABASE & BẢO MẬT ---
SUPABASE_URL = "https://ymjwfregjyndewmlzhvk.supabase.co"
SUPABASE_KEY = "sb_publishable_RlsBLKOJsnkBK2AhRGNlDA_6xN1y9HI" 
PASSWORD_CO_GIAO = "123qwe" # Mật khẩu đăng nhập phần mềm

# --- CẤU HÌNH API KEY CHO TRỢ LÝ AI (Đã tích hợp sẵn của bạn) ---
DEFAULT_GEMINI_API_KEY = "AIzaSyDbYJg_-S9_1_Nkkc6zG1KZUWmaAKfo7RY"

try:
    from supabase import create_client, Client
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
except Exception as e:
    st.error(f"⚠️ Lỗi kết nối Supabase: {e}")

st.set_page_config(page_title="English Teacher Assistant", page_icon="👩‍🏫", layout="wide")

if not os.path.exists("kho_tai_lieu"):
    os.makedirs("kho_tai_lieu")

# --- HỆ THỐNG ĐĂNG NHẬP BẢO MẬT ---
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

if not st.session_state["authenticated"]:
    st.title("🔒 ĐĂNG NHẬP HỆ THỐNG QUẢN LÝ")
    st.info("Vui lòng nhập mật khẩu của cô giáo để truy cập phần mềm.")
    with st.form("login_form"):
        pw_input = st.text_input("Mật khẩu truy cập:", type="password")
        if st.form_submit_button("Đăng Nhập"):
            if pw_input == PASSWORD_CO_GIAO:
                st.session_state["authenticated"] = True
                st.rerun()
            else:
                st.error("❌ Mật khẩu không chính xác!")
    st.stop()

# --- THANH MENU BÊN TRÁI ---
st.sidebar.title("👩‍🏫 MENU QUẢN LÝ")
if st.sidebar.button("🔓 Đăng Xuất"):
    st.session_state["authenticated"] = False
    st.rerun()
st.sidebar.markdown("---")
menu = ["🏠 Trang Chủ", "🎓 Quản lý Lớp & Học Sinh", "💰 Điểm danh & Học phí", "📚 Không gian Giáo án", "🤖 Trợ lý AI (Tạo bài tập)"]
choice = st.sidebar.radio("Vui lòng chọn chức năng:", menu)
st.sidebar.markdown("---")
st.sidebar.info("Phần mềm hỗ trợ giảng dạy Tiếng Anh.\nĐám mây Supabase ☁️ & Trợ lý AI 🤖")

# ==================== ĐIỀU HƯỚNG CÁC TRANG ====================
if choice == "🏠 Trang Chủ":
    st.title("Chào mừng đến với Hệ thống Quản lý Giảng dạy! 🌟")
    try:
        res_classes = supabase.table("classes").select("*", count="exact").eq("status", "Đang hoạt động").execute()
        res_students = supabase.table("students").select("*", count="exact").eq("status", "Đang học").execute()
        total_classes = len(res_classes.data) if res_classes.data else 0
        total_students = len(res_students.data) if res_students.data else 0
    except:
        total_classes, total_students = 0, 0

    col1, col2, col3 = st.columns(3)
    col1.metric("Lớp đang hoạt động", f"{total_classes} Lớp")
    col2.metric("Học sinh đang học", f"{total_students} Học sinh")
    col3.metric("Hệ thống Cloud", "Đã kết nối ☁️")

elif choice == "🎓 Quản lý Lớp & Học Sinh":
    st.title("🎓 Quản lý Lớp học & Danh sách Học sinh")
    tab_lop, tab_hocsinh = st.tabs(["📁 Quản lý Lớp Học", "👨‍🎓 Quản lý Học Sinh"])
    
    with tab_lop:
        with st.expander("➕ Bấm vào đây để THÊM LỚP MỚI", expanded=False):
            with st.form("form_them_lop", clear_on_submit=True):
                c1, c2, c3 = st.columns(3)
                with c1: class_name = st.text_input("Tên Lớp (VD: Két 1)")
                with c2: schedule = st.text_input("Lịch học")
                with c3: tuition_fee = st.number_input("Học phí / Buổi (VNĐ)", min_value=0, step=10000, value=50000)
                if st.form_submit_button("Lưu Lớp Học") and class_name.strip():
                    supabase.table("classes").insert({"class_name": class_name, "schedule": schedule, "tuition_fee": tuition_fee, "status": "Đang hoạt động"}).execute()
                    st.success("✅ Đã thêm lớp lên mây!"); st.rerun()

        with st.expander("✏️ Bấm vào đây để SỬA / XÓA thông tin Lớp học", expanded=False):
            res_c = supabase.table("classes").select("*").execute()
            if res_c.data:
                classes_df_all = pd.DataFrame(res_c.data)
                class_options = classes_df_all.apply(lambda x: f"{x['class_name']} ({x['status']}) - ID:{x['id']}", axis=1).tolist()
                sel_class_str = st.selectbox("🔍 Tìm chọn lớp cần xử lý:", class_options)
                sel_class_id = int(sel_class_str.split("ID:")[-1])
                curr_c_data = classes_df_all[classes_df_all['id'] == sel_class_id].iloc[0]
                
                with st.form("edit_class_form"):
                    c1, c2, c3 = st.columns(3)
                    with c1: e_c_name = st.text_input("Tên Lớp", value=curr_c_data['class_name'])
                    with c2: e_c_sched = st.text_input("Lịch học", value=curr_c_data['schedule'] if curr_c_data['schedule'] else "")
                    with c3: e_c_fee = st.number_input("Học phí / Buổi", min_value=0, step=10000, value=int(curr_c_data['tuition_fee']))
                    e_c_status = st.radio("Trạng thái Lớp:", ["Đang hoạt động", "Đã đóng"], index=0 if curr_c_data['status']=="Đang hoạt động" else 1, horizontal=True)
                    st.markdown("---")
                    del_class_confirm = st.checkbox("⚠️ Xác nhận XÓA VĨNH VIỄN lớp này")
                    btn1, btn2 = st.columns(2)
                    if btn1.form_submit_button("💾 Lưu Cập Nhật"):
                        supabase.table("classes").update({"class_name": e_c_name, "schedule": e_c_sched, "tuition_fee": e_c_fee, "status": e_c_status}).eq("id", sel_class_id).execute()
                        st.success("✅ Đã cập nhật!"); st.rerun()
                    if btn2.form_submit_button("🗑️ Xóa Lớp"):
                        if del_class_confirm:
                            res_chk = supabase.table("students").select("*", count="exact").eq("class_id", sel_class_id).execute()
                            if res_chk.data and len(res_chk.data) > 0:
                                st.error("❌ Lớp đang có học sinh. Vui lòng chuyển sang 'Đã đóng'!")
                            else:
                                supabase.table("classes").delete().eq("id", sel_class_id).execute()
                                st.success("✅ Đã xóa!"); st.rerun()
                        else: st.error("⚠️ Phải tích xác nhận trước khi xóa.")
            else: st.info("Chưa có lớp.")
        
        st.subheader("📋 Danh Sách Các Lớp")
        res_c = supabase.table("classes").select("*").execute()
        if res_c.data:
            df_c = pd.DataFrame(res_c.data)[['id', 'class_name', 'schedule', 'tuition_fee', 'status']]
            df_c.columns = ['ID', 'Tên Lớp', 'Lịch Học', 'Học Phí', 'Trạng Thái']
            st.dataframe(df_c, use_container_width=True, hide_index=True)

    with tab_hocsinh:
        res_c_act = supabase.table("classes").select("id, class_name").eq("status", "Đang hoạt động").execute()
        res_c_all = supabase.table("classes").select("id, class_name").execute()
        
        with st.expander("➕ Bấm vào đây để THÊM HỌC SINH MỚI", expanded=False):
            if res_c_act.data:
                with st.form("form_them_hs", clear_on_submit=True):
                    c1, c2 = st.columns(2)
                    with c1:
                        class_map_act = {item['class_name']: item['id'] for item in res_c_act.data}
                        sel_cls = st.selectbox("Chọn Lớp", list(class_map_act.keys()))
                        fname = st.text_input("Họ và Tên Học Sinh")
                        pname = st.text_input("Tên Phụ Huynh")
                    with c2:
                        phone = st.text_input("Số điện thoại")
                        status = st.selectbox("Trạng thái", ["Đang học", "Bảo lưu", "Đã nghỉ"])
                        if st.form_submit_button("Lưu Học Sinh") and fname.strip():
                            supabase.table("students").insert({"class_id": class_map_act[sel_cls], "full_name": fname, "parent_name": pname, "phone": phone, "status": status}).execute()
                            st.success("✅ Đã thêm học sinh lên mây!"); st.rerun()
            else: st.warning("Vui lòng tạo ít nhất 1 Lớp 'Đang hoạt động' trước!")

        with st.expander("✏️ Bấm vào đây để SỬA / XÓA thông tin Học sinh", expanded=False):
            res_st_all = supabase.table("students").select("id, full_name, phone, class_id, parent_name, status").execute()
            if res_st_all.data and res_c_all.data:
                st_df = pd.DataFrame(res_st_all.data)
                class_map_all = {item['id']: item['class_name'] for item in res_c_all.data}
                st_options = st_df.apply(lambda x: f"{x['full_name']} - {class_map_all.get(x['class_id'], 'Không rõ')} (ID:{x['id']})", axis=1).tolist()
                sel_st_str = st.selectbox("🔍 Tìm chọn học sinh cần xử lý:", st_options)
                sel_st_id = int(sel_st_str.split("(ID:")[-1].replace(")", ""))
                curr_data = st_df[st_df['id'] == sel_st_id].iloc[0]
                
                with st.form("edit_hs_form"):
                    c1, c2 = st.columns(2)
                    with c1:
                        rev_class_map = {v: k for k, v in class_map_all.items()}
                        e_class_name = st.selectbox("Đổi Lớp", list(class_map_all.values()), index=list(class_map_all.values()).index(class_map_all.get(curr_data['class_id'], '')))
                        e_fname = st.text_input("Họ và Tên", value=curr_data['full_name'])
                        e_pname = st.text_input("Tên Phụ Huynh", value=curr_data['parent_name'] if curr_data['parent_name'] else "")
                    with c2:
                        e_phone = st.text_input("Số điện thoại", value=curr_data['phone'] if curr_data['phone'] else "")
                        e_status = st.selectbox("Trạng thái", ["Đang học", "Bảo lưu", "Đã nghỉ"], index=["Đang học", "Bảo lưu", "Đã nghỉ"].index(curr_data['status']))
                        st.markdown("---")
                        del_confirm = st.checkbox("⚠️ Xác nhận xóa hoàn toàn học sinh này")
                    
                    c_btn1, c_btn2 = st.columns(2)
                    if c_btn1.form_submit_button("💾 Lưu Cập Nhật"):
                        new_class_id = rev_class_map[e_class_name]
                        supabase.table("students").update({"class_id": new_class_id, "full_name": e_fname, "parent_name": e_pname, "phone": e_phone, "status": e_status}).eq("id", sel_st_id).execute()
                        st.success("✅ Đã cập nhật!"); st.rerun()
                    if c_btn2.form_submit_button("🗑️ Xóa Học Sinh"):
                        if del_confirm:
                            supabase.table("attendance").delete().eq("student_id", sel_st_id).execute()
                            supabase.table("tuition_payments").delete().eq("student_id", sel_st_id).execute()
                            supabase.table("students").delete().eq("id", sel_st_id).execute()
                            st.success("✅ Đã xóa!"); st.rerun()
                        else: st.error("⚠️ Tích xác nhận trước khi xóa!")

        st.subheader("📋 Bảng Danh Sách Học Sinh")
        res_join = supabase.table("students").select("id, full_name, parent_name, phone, status, classes(class_name)").execute()
        if res_join.data:
            flat_st = []
            for row in res_join.data:
                flat_st.append({
                    "ID": row['id'], "Họ và Tên": row['full_name'], "Tên Phụ Huynh": row['parent_name'] if row['parent_name'] else "",
                    "Lớp": row['classes']['class_name'] if row['classes'] else "Không rõ",
                    "SĐT": row['phone'] if row['phone'] else "", "Trạng Thái": row['status']
                })
            df_st_full = pd.DataFrame(flat_st)
            
            col_f1, col_f2, col_f3 = st.columns(3)
            with col_f1:
                class_filter_options = ["Tất cả các lớp"] + list(class_map_all.values()) if res_c_all.data else ["Tất cả các lớp"]
                sel_filter_class = st.selectbox("📌 Lọc theo Lớp", class_filter_options)
            with col_f2: sel_filter_status = st.selectbox("📌 Lọc theo Trạng thái", ["Tất cả", "Đang học", "Bảo lưu", "Đã nghỉ"])
            with col_f3: search_text = st.text_input("🔍 Tìm Tên / SĐT")
            
            if sel_filter_class != "Tất cả các lớp":
                df_st_full = df_st_full[df_st_full['Lớp'] == sel_filter_class]
            if sel_filter_status != "Tất cả":
                df_st_full = df_st_full[df_st_full['Trạng Thái'] == sel_filter_status]
            if search_text.strip():
                mask = df_st_full['Họ và Tên'].str.contains(search_text, case=False, na=False) | df_st_full['SĐT'].str.contains(search_text, case=False, na=False)
                df_st_full = df_st_full[mask]
                
            st.markdown(f"*(Tìm thấy: **{len(df_st_full)}** học sinh)*")
            st.dataframe(df_st_full, use_container_width=True, hide_index=True)
        else:
            st.info("Chưa có học sinh nào.")

elif choice == "💰 Điểm danh & Học phí":
    st.title("💰 Điểm danh & Quản lý Học phí trên Cloud")
    res_c_all = supabase.table("classes").select("*").execute()
    if not res_c_all.data:
        st.warning("⚠️ Chưa có lớp học nào.")
    else:
        tab_diemdanh, tab_lichsu, tab_hocphi, tab_baocao = st.tabs(["📝 Chấm Điểm danh", "🗓️ Lịch sử & Tra cứu", "💵 Tính phí & Đòi Tiền", "📊 Báo cáo Doanh thu"])
        classes_df = pd.DataFrame(res_c_all.data)
        class_display_names = classes_df.apply(lambda x: f"{x['class_name']} {'(Đã đóng)' if x['status']=='Đã đóng' else ''}", axis=1)
        class_dict = dict(zip(class_display_names, classes_df['id']))
        
        with tab_diemdanh:
            c1, c2 = st.columns([1, 1])
            with c1: selected_class_attend = st.selectbox("Chọn Lớp điểm danh", list(class_dict.keys()), key="c_att")
            with c2: selected_date = st.date_input("Ngày học", datetime.date.today())
            class_id_attend = class_dict[selected_class_attend]
            
            res_st_att = supabase.table("students").select("id, full_name, parent_name, phone").eq("class_id", class_id_attend).eq("status", "Đang học").execute()
            if not res_st_att.data:
                st.info("Lớp này chưa có học sinh nào đang học.")
            else:
                students_df = pd.DataFrame(res_st_att.data)
                st.markdown(f"**Danh sách lớp: {selected_class_attend} - Ngày {selected_date.strftime('%d/%m/%Y')}**")
                
                res_att_date = supabase.table("attendance").select("student_id, status, note").eq("date", str(selected_date)).execute()
                att_dict = {item['student_id']: item for item in res_att_date.data} if res_att_date.data else {}
                
                with st.form("form_diemdanh"):
                    col1, col2, col3, col4, col5 = st.columns([1.5, 1.5, 1.5, 2.5, 1.5])
                    col1.markdown("**Tên Học Sinh**"); col2.markdown("**Tên Phụ Huynh**"); col3.markdown("**Số Điện Thoại**"); col4.markdown("**Điểm Danh**"); col5.markdown("**Ghi Chú**")
                    st.markdown("---")
                    
                    attend_data = {}
                    for _, row in students_df.iterrows():
                        s_id = row['id']
                        old_rec = att_dict.get(s_id, {"status": "Có mặt", "note": ""})
                        d_st = old_rec['status']
                        d_nt = old_rec['note']
                        
                        c1, c2, c3, c4, c5 = st.columns([1.5, 1.5, 1.5, 2.5, 1.5])
                        with c1: u_name = st.text_input("Tên", value=row['full_name'], key=f"n_{s_id}", label_visibility="collapsed")
                        with c2: u_pname = st.text_input("PH", value=row['parent_name'] if row['parent_name'] else "", key=f"p_{s_id}", placeholder="Nhập PH...", label_visibility="collapsed")
                        with c3: u_phone = st.text_input("SĐT", value=row['phone'] if row['phone'] else "", key=f"ph_{s_id}", placeholder="Nhập SĐT...", label_visibility="collapsed")
                        with c4: 
                            idx_st = ["Có mặt", "Vắng mặt", "Nghỉ có phép"].index(d_st) if d_st in ["Có mặt", "Vắng mặt", "Nghỉ có phép"] else 0
                            u_status = st.radio("TT", ["Có mặt", "Vắng", "Có phép"], index=0 if idx_st==0 else (1 if idx_st==1 else 2), key=f"st_{s_id}", horizontal=True, label_visibility="collapsed")
                        with c5: u_note = st.text_input("GC", value=d_nt, key=f"nt_{s_id}", placeholder="Ghi chú...", label_visibility="collapsed")
                        
                        attend_data[s_id] = {'name': u_name, 'pname': u_pname, 'phone': u_phone, 'status': u_status.replace("Vắng", "Vắng mặt").replace("Có phép", "Nghỉ có phép"), 'note': u_note}
                            
                    st.markdown("---")
                    if st.form_submit_button("💾 Lưu Điểm Danh & Cập Nhật"):
                        for s_id, data in attend_data.items():
                            supabase.table("students").update({"full_name": data['name'], "parent_name": data['pname'], "phone": data['phone']}).eq("id", s_id).execute()
                            res_chk_att = supabase.table("attendance").select("id").eq("student_id", s_id).eq("date", str(selected_date)).execute()
                            if res_chk_att.data and len(res_chk_att.data) > 0:
                                supabase.table("attendance").update({"status": data['status'], "note": data['note']}).eq("student_id", s_id).eq("date", str(selected_date)).execute()
                            else:
                                supabase.table("attendance").insert({"student_id": s_id, "date": str(selected_date), "status": data['status'], "note": data['note']}).execute()
                        st.success("✅ Đã lưu điểm danh lên mây thành công!"); st.rerun()

        with tab_lichsu:
            st.subheader("🗓️ Tra cứu lịch sử điểm danh theo ngày")
            c_hist1, c_hist2 = st.columns([1, 1])
            with c_hist1:
                selected_class_hist = st.selectbox("1. Chọn Lớp cần tra cứu:", list(class_dict.keys()), key="c_hist")
                class_id_hist = class_dict[selected_class_hist]
            
            res_st_cls = supabase.table("students").select("id").eq("class_id", class_id_hist).execute()
            if not res_st_cls.data:
                st.info("Lớp này chưa có học sinh.")
            else:
                st_ids = [item['id'] for item in res_st_cls.data]
                res_att_all = supabase.table("attendance").select("date").in_("student_id", st_ids).execute()
                if not res_att_all.data:
                    st.info("Lớp này chưa có lịch sử điểm danh.")
                else:
                    dates_list = sorted(list(set([item['date'] for item in res_att_all.data])), reverse=True)
                    dates_df = pd.DataFrame({'date': dates_list})
                    dates_df['display_date'] = pd.to_datetime(dates_df['date']).dt.strftime('%d/%m/%Y')
                    date_mapping = dict(zip(dates_df['display_date'], dates_df['date']))
                    
                    with c_hist2:
                        selected_display_date = st.selectbox("2. Chọn ngày đã học:", list(date_mapping.keys()))
                        selected_actual_date = date_mapping[selected_display_date]
                    
                    res_hist = supabase.table("attendance").select("status, note, students(full_name, phone)").eq("date", selected_actual_date).in_("student_id", st_ids).execute()
                    if res_hist.data:
                        hist_rows = []
                        for r in res_hist.data:
                            if r['students']:
                                hist_rows.append({
                                    "Họ và Tên": r['students']['full_name'], "SĐT": r['students']['phone'] if r['students']['phone'] else "",
                                    "Trạng thái": ('🟢 Có mặt' if r['status']=='Có mặt' else ('🔴 Vắng mặt' if r['status']=='Vắng mặt' else '🟡 Nghỉ có phép')),
                                    "Ghi chú": r['note'] if r['note'] else ""
                                })
                        hist_df = pd.DataFrame(hist_rows)
                        total_hs = len(hist_df)
                        total_comat = len(hist_df[hist_df['Trạng thái'].str.contains('Có mặt')])
                        total_vang = total_hs - total_comat
                        
                        st.markdown("---")
                        m1, m2, m3 = st.columns(3)
                        m1.metric("Sĩ số", f"{total_hs} HS")
                        m2.metric("🟢 Đi học", f"{total_comat} HS")
                        m3.metric("🔴 Nghỉ", f"{total_vang} HS")
                        st.dataframe(hist_df, use_container_width=True, hide_index=True)

        with tab_hocphi:
            c1, c2, c3 = st.columns(3)
            current_month = datetime.date.today().month
            current_year = datetime.date.today().year
            with c1: sel_month = st.selectbox("Tháng", range(1, 13), index=current_month-1)
            with c2: sel_year = st.selectbox("Năm", [current_year-1, current_year, current_year+1], index=1)
            with c3: sel_class_fee = st.selectbox("Lớp", list(class_dict.keys()), key="c_fee")
                
            class_id_fee = class_dict[sel_class_fee]
            fee_per_session = float(classes_df[classes_df['id'] == class_id_fee]['tuition_fee'].values[0])
            month_str = f"{sel_year}-{sel_month:02d}"
            
            res_fee_st = supabase.table("students").select("id, full_name, parent_name").eq("class_id", class_id_fee).eq("status", "Đang học").execute()
            if res_fee_st.data:
                fee_students = res_fee_st.data
                res_tp = supabase.table("tuition_payments").select("*").eq("month", month_str).execute()
                tp_dict = {item['student_id']: item for item in res_tp.data} if res_tp.data else {}
                
                res_att_m = supabase.table("attendance").select("student_id, date, status").like("date", f"{month_str}-%").execute()
                att_m_list = res_att_m.data if res_att_m.data else []
                
                fee_rows = []
                for st_item in fee_students:
                    st_id = st_item['id']
                    st_atts = [a for a in att_m_list if a['student_id'] == st_id]
                    comat = len([a for a in st_atts if a['status'] == 'Có mặt'])
                    nghi = len([a for a in st_atts if a['status'] != 'Có mặt'])
                    nghi_dates = ", ".join([a['date'][8:10] + "/" + a['date'][5:7] for a in st_atts if a['status'] != 'Có mặt'])
                    
                    tp_rec = tp_dict.get(st_id, {})
                    extra = float(tp_rec.get('extra_fee', 0))
                    discount = float(tp_rec.get('discount', 0))
                    status_pay = tp_rec.get('status', '❌ Chưa đóng')
                    
                    goc = fee_per_session * comat
                    thucthu = goc + extra - discount
                    
                    fee_rows.append({
                        "student_id": st_id, "Họ Tên Học Sinh": st_item['full_name'], "Tên Phụ Huynh": st_item['parent_name'] if st_item['parent_name'] else "",
                        "Có mặt (buổi)": comat, "Nghỉ (buổi)": nghi, "Các ngày nghỉ": nghi_dates,
                        "Học phí gốc": goc, "Phụ thu": extra, "Giảm trừ": discount, "THỰC THU": thucthu, "Trạng Thái": status_pay
                    })
                
                fee_df = pd.DataFrame(fee_rows)
                display_df = fee_df.drop(columns=['student_id'])
                for col in ['Học phí gốc', 'Phụ thu', 'Giảm trừ', 'THỰC THU']:
                    display_df[col] = display_df[col].apply(lambda x: f"{int(x):,}")
                st.markdown(f"### Bảng kê học phí tháng {sel_month}/{sel_year} - {sel_class_fee}")
                st.dataframe(display_df, use_container_width=True, hide_index=True)
                
                st.markdown("---")
                col_left, col_right = st.columns([1, 1])
                with col_left:
                    st.subheader("💳 Cập nhật Thu Tiền")
                    unpaid_df = fee_df[fee_df['Trạng Thái'] == '❌ Chưa đóng']
                    if unpaid_df.empty:
                        st.success("🎉 Toàn bộ học sinh đã đóng đủ học phí!")
                    else:
                        unpaid_dict = dict(zip(unpaid_df['Họ Tên Học Sinh'], unpaid_df['student_id']))
                        with st.form("form_thu_tien"):
                            st_pay_name = st.selectbox("Chọn học sinh nộp tiền:", list(unpaid_dict.keys()))
                            c_f1, c_f2 = st.columns(2)
                            with c_f1: extra_in = st.number_input("Phụ thu", min_value=0, step=10000, value=0)
                            with c_f2: disc_in = st.number_input("Giảm trừ", min_value=0, step=10000, value=0)
                            if st.form_submit_button("✅ Xác nhận Đã Thu Tiền"):
                                s_id_p = unpaid_dict[st_pay_name]
                                supabase.table("tuition_payments").upsert({
                                    "student_id": s_id_p, "month": month_str, "status": "✅ Đã đóng", "extra_fee": extra_in, "discount": disc_in
                                }, on_conflict="student_id,month").execute()
                                st.success("✅ Đã cập nhật thu tiền lên mây!"); st.rerun()
                with col_right:
                    st.subheader("💬 Tạo tin nhắn Zalo gửi Phụ Huynh")
                    zalo_st = st.selectbox("Chọn học sinh báo phí:", list(fee_df['Họ Tên Học Sinh']))
                    if zalo_st:
                        z_row = fee_df[fee_df['Họ Tên Học Sinh'] == zalo_st].iloc[0]
                        p_name_z = z_row['Tên Phụ Huynh'] if z_row['Tên Phụ Huynh'] else "Phụ huynh bé " + zalo_st
                        msg = f"Kính gửi {p_name_z},\n\nCô xin thông báo học phí tháng {sel_month} của bé {zalo_st} (Lớp {sel_class_fee}):\n- Số buổi đi học: {z_row['Có mặt (buổi)']} buổi\n"
                        if z_row['Nghỉ (buổi)'] > 0: msg += f"- Số buổi nghỉ: {z_row['Nghỉ (buổi)']} buổi (Ngày: {z_row['Các ngày nghỉ']})\n"
                        msg += f"- Học phí gốc: {int(z_row['Học phí gốc']):,} VNĐ\n"
                        if z_row['Phụ thu'] > 0: msg += f"- Phụ thu: +{int(z_row['Phụ thu']):,} VNĐ\n"
                        if z_row['Giảm trừ'] > 0: msg += f"- Giảm trừ: -{int(z_row['Giảm trừ']):,} VNĐ\n"
                        msg += f"\n💰 TỔNG THỰC THU: {int(z_row['THỰC THU']):,} VNĐ\n\nChuyển khoản STK: [STK của cô]\nNội dung: {z_row['Họ Tên Học Sinh']} lop {sel_class_fee} thang {sel_month}\n\nCảm ơn PH!"
                        st.code(msg, language="text")
            else: st.info("Lớp chưa có học sinh.")

        with tab_baocao:
            st.subheader("📊 Báo cáo Doanh Thu Tổng Quát")
            current_year = datetime.date.today().year
            c_rep1, c_rep2 = st.columns(2)
            with c_rep1: rep_year = st.selectbox("📅 Chọn Năm báo cáo", [current_year-1, current_year, current_year+1], index=1, key="rep_y")
            with c_rep2: rep_month = st.selectbox("📆 Chọn Tháng xem chi tiết", range(1, 13), index=current_month-1, key="rep_m")
            
            rep_month_str = f"{rep_year}-{rep_month:02d}"
            res_rep = supabase.table("tuition_payments").select("student_id, month, extra_fee, discount").eq("status", "✅ Đã đóng").like("month", f"{rep_year}-%").execute()
            
            if not res_rep.data:
                st.warning(f"Chưa có dữ liệu thu tiền nào trong năm {rep_year}.")
            else:
                tp_list = res_rep.data
                res_cls_all = supabase.table("classes").select("id, class_name, tuition_fee").execute()
                cls_map = {c['id']: c for c in res_cls_all.data} if res_cls_all.data else {}
                
                res_st_all = supabase.table("students").select("id, full_name, class_id").execute()
                st_map = {s['id']: s for s in res_st_all.data} if res_st_all.data else {}
                
                res_att_year = supabase.table("attendance").select("student_id, date, status").eq("status", "Có mặt").like("date", f"{rep_year}-%").execute()
                att_year_list = res_att_year.data if res_att_year.data else []
                
                report_rows = []
                for tp in tp_list:
                    s_id = tp['student_id']
                    m_tp = tp['month']
                    if s_id in st_map:
                        st_info = st_map[s_id]
                        c_id = st_info['class_id']
                        if c_id in cls_map:
                            cls_info = cls_map[c_id]
                            fee_p = float(cls_info['tuition_fee'])
                            count_p = len([a for a in att_year_list if a['student_id'] == s_id and a['date'].startswith(m_tp)])
                            rev = (count_p * fee_p) + float(tp['extra_fee']) - float(tp['discount'])
                            report_rows.append({
                                "month": m_tp,
                                "class_name": cls_info['class_name'],
                                "Thực thu": rev
                            })
                
                if not report_rows:
                    st.warning(f"Chưa đủ dữ liệu điểm danh tương ứng với các khoản đã thu trong năm {rep_year}.")
                else:
                    df_rep = pd.DataFrame(report_rows)
                    total_year = df_rep['Thực thu'].sum()
                    
                    df_month = df_rep[df_rep['month'] == rep_month_str]
                    total_month = df_month['Thực thu'].sum() if not df_month.empty else 0
                    
                    class_month_summary = pd.DataFrame()
                    if not df_month.empty:
                        class_month_summary = df_month.groupby('class_name')['Thực thu'].sum().reset_index().sort_values(by='Thực thu', ascending=False)
                    
                    st.markdown("---")
                    m_rep1, m_rep2, m_rep3 = st.columns(3)
                    m_rep1.metric(f"💰 TỔNG THU THÁNG {rep_month}", f"{int(total_month):,} VNĐ")
                    m_rep2.metric(f"🏆 TỔNG DOANH THU NĂM {rep_year}", f"{int(total_year):,} VNĐ")
                    
                    top_class = class_month_summary.iloc[0]['class_name'] if not class_month_summary.empty else "Chưa có"
                    top_class_rev = class_month_summary.iloc[0]['Thực thu'] if not class_month_summary.empty else 0
                    m_rep3.metric(f"🔥 LỚP TOP 1 (Tháng {rep_month})", top_class, f"{int(top_class_rev):,} VNĐ")
                    
                    st.markdown("---")
                    c_chart1, c_chart2 = st.columns(2)
                    with c_chart1:
                        st.markdown(f"**Doanh thu chi tiết theo lớp (Tháng {rep_month})**")
                        if not class_month_summary.empty:
                            class_display = class_month_summary.rename(columns={'class_name':'Tên Lớp', 'Thực thu': 'Doanh Thu'})
                            class_display['Doanh Thu'] = class_display['Doanh Thu'].apply(lambda x: f"{int(x):,} VNĐ")
                            st.dataframe(class_display, use_container_width=True, hide_index=True)
                        else: 
                            st.info(f"Tháng {rep_month} chưa có dữ liệu thu tiền.")
                    with c_chart2:
                        st.markdown(f"**Biểu đồ Doanh thu các tháng (Năm {rep_year})**")
                        month_summary = df_rep.groupby('month')['Thực thu'].sum().reset_index()
                        if not month_summary.empty:
                            st.bar_chart(month_summary.rename(columns={'Thực thu': 'Doanh thu (VNĐ)'}).set_index('month'))
                        else: 
                            st.info("Chưa đủ dữ liệu để vẽ biểu đồ.")

elif choice == "📚 Không gian Giáo án":
    st.title("📚 Không gian Giáo trình & Tài liệu trên Cloud")
    res_c_act = supabase.table("classes").select("id, class_name").execute()
    if res_c_act.data:
        class_dict_doc = {item['class_name']: item['id'] for item in res_c_act.data}
        sel_c_doc = st.selectbox("📌 Chọn Lớp:", list(class_dict_doc.keys()))
        c_id_d = class_dict_doc[sel_c_doc]
        
        tab_gt, tab_bt, tab_dt, tab_khac = st.tabs(["📚 Giáo Trình", "📝 Bài Tập", "✍️ Đề Thi Thử", "🎧 Audio / Khác"])
        cats = {"📚 Giáo Trình": tab_gt, "📝 Bài Tập": tab_bt, "✍️ Đề Thi Thử": tab_dt, "🎧 Audio / Khác": tab_khac}
        
        for cat, t_w in cats.items():
            with t_w:
                c1, c2 = st.columns([1, 2])
                with c1:
                    up_f = st.file_uploader(f"Tải lên mục {cat}", key=f"up_{c_id_d}_{cat}")
                    if st.button("💾 Lưu File", key=f"sv_{c_id_d}_{cat}"):
                        if up_f:
                            s_name = f"{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}_{up_f.name}"
                            s_path = os.path.join("kho_tai_lieu", s_name)
                            with open(s_path, "wb") as f: f.write(up_f.getbuffer())
                            supabase.table("documents").insert({
                                "class_id": c_id_d, "category": cat, "file_name": up_f.name,
                                "file_path": s_path, "upload_date": datetime.datetime.now().strftime('%d/%m/%Y %H:%M')
                            }).execute()
                            st.success("✅ Đã tải file lên mây!"); st.rerun()
                with c2:
                    res_docs = supabase.table("documents").select("*").eq("class_id", c_id_d).eq("category", cat).execute()
                    if res_docs.data:
                        for doc in res_docs.data:
                            dc1, dc2, dc3 = st.columns([5, 1.5, 1])
                            dc1.markdown(f"📄 **{doc['file_name']}** *(Ngày: {doc['upload_date']})*")
                            try:
                                with open(doc['file_path'], "rb") as f:
                                    dc2.download_button("⬇️ Tải Về", f, file_name=doc['file_name'], key=f"dl_{doc['id']}")
                            except: dc2.error("Lỗi file")
                            if dc3.button("🗑️ Xóa", key=f"del_{doc['id']}"):
                                if os.path.exists(doc['file_path']): os.remove(doc['file_path'])
                                supabase.table("documents").delete().eq("id", doc['id']).execute()
                                st.rerun()
                            st.markdown("---")
    else: st.info("Chưa có lớp học.")

elif choice == "🤖 Trợ lý AI (Tạo bài tập)":
    st.title("🤖 Trợ lý AI - Soạn Đề Thi Chuyên Lạng Sơn")
    st.info("💡 Trợ lý AI đã được kích hoạt sẵn sàng hỗ trợ cô giáo soạn bài tập, đề thi nhanh chóng!")
    
    try:
        import google.generativeai as genai
        
        genai.configure(api_key=DEFAULT_GEMINI_API_KEY)
        task = st.selectbox("📌 Chọn loại bài tập:", [
            "10 câu Trắc nghiệm ABCD", 
            "Điền từ vào chỗ trống", 
            "Viết lại câu", 
            "Đề thi thử vào 10 chuyên Lạng Sơn"
        ])
        user_in = st.text_area("📝 Nhập yêu cầu cụ thể:", placeholder="Ví dụ: Tạo đề thi thử bám sát đề chuyên Chu Văn An Lạng Sơn...")
        
        if st.button("🚀 Kích hoạt AI tạo đề"):
            if user_in.strip() == "":
                st.error("⚠️ Vui lòng nhập nội dung yêu cầu trước!")
            else:
                with st.spinner("🤖 AI đang tự động soạn đề thi..."):
                    try:
                        models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
                        mod = models[0] if models else 'gemini-pro'
                        for m in models:
                            if 'flash' in m.lower(): mod = m; break
                        
                        prompt = f"""
                        Bạn là một chuyên gia giáo dục và giáo viên tiếng Anh xuất sắc. Hãy thực hiện yêu cầu sau:
                        LOẠI BÀI TẬP: {task}
                        YÊU CẦU CHI TIẾT: {user_in}
                        HƯỚNG DẪN: Trình bày rõ ràng, đẹp mắt, bắt buộc có phần ĐÁP ÁN chi tiết ở cuối.
                        """
                        res = genai.GenerativeModel(mod).generate_content(prompt)
                        st.success("🎉 Đã soạn xong đề thi! Cô giáo có thể Copy để sử dụng.")
                        st.markdown("---")
                        st.markdown(res.text)
                    except Exception as e:
                        st.error(f"⚠️ Lỗi kết nối AI: {e}")
    except ImportError:
        st.error("⚠️ Lỗi: Thư viện `google-generativeai` chưa được cài đặt trên hệ thống Cloud. Hãy đảm bảo bạn đã thêm nó vào file `requirements.txt` trên GitHub.")
