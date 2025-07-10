import streamlit as st
import pandas as pd

# 计算奖金的核心函数，完全复刻你原代码逻辑（去掉密码和注释）
def calculate_bonus(dir_docs, docs, rest_docs, new_docs,
                    xiaoyi_1, xiaoyi_2, fubu, xinzang, chanke,
                    hospital_pingjun):

    rest_docs_prize = sum(d["奖金"] for d in rest_docs)
    new_docs_prize = sum(d["奖金"] for d in new_docs)

    shangji = len(dir_docs) + len(docs)

    pingjun1 = xiaoyi_1 * 0.2
    pingjun2 = xiaoyi_2 * 0.2
    pingjun_total = pingjun1 + pingjun2
    pingjun_single = pingjun_total / max(len(docs),1)  # 防止除0

    jiangli = pingjun_single * 0.2 * 3

    total_papers = sum(doc["报告数"] for doc in docs)
    total_works = sum(doc["工作量"] for doc in docs) - total_papers * 9  # 减图文费用

    total_fubu = sum(doc["腹部"] for doc in docs)
    total_xinzang = sum(doc["心脏"] for doc in docs)
    total_chanke = sum(doc["产科"] for doc in docs)

    # 调整效益，去掉休息医生奖金、李珊珊奖金、老总补贴600，新职工奖金
    xiaoyi_1 = xiaoyi_1 - rest_docs_prize/2 - 600 - hospital_pingjun - (new_docs_prize/2)
    xiaoyi_2 = xiaoyi_2 - rest_docs_prize/2 - 2000 - (new_docs_prize/2)

    # 程主任效益分配
    cheng_1 = xiaoyi_1 / shangji * 1.5
    cheng_2 = xiaoyi_2 / shangji * 1.5
    cheng_tot = cheng_1 + cheng_2

    # 其他人员效益减去主任奖金和平均奖、奖励
    xiaoyi_1 = xiaoyi_1 - cheng_1 - pingjun1 - jiangli/2
    xiaoyi_2 = xiaoyi_2 - cheng_2 - pingjun2 - jiangli/2

    def jisuan1(doc):
        return (doc["工作量"] - doc["报告数"] * 9) / total_works * xiaoyi_1 if total_works else 0

    def jisuan2(doc):
        return doc["报告数"] / total_papers * xiaoyi_2 if total_papers else 0

    def jisuan3(doc):
        return doc["腹部"] / total_fubu * fubu if total_fubu else 0

    def jisuan4(doc):
        return doc["心脏"] / total_xinzang * xinzang if total_xinzang else 0

    def jisuan5(doc):
        return doc["产科"] / total_chanke * chanke if total_chanke else 0

    # 普通医生奖金计算
    normal_results = []
    sum_doc = 0
    for doc in docs:
        prize = (
            jisuan1(doc) + jisuan2(doc) + jisuan3(doc) +
            jisuan4(doc) + jisuan5(doc) + pingjun_single + 11
        )
        normal_results.append({"姓名": doc["姓名"], "奖金": prize})
        sum_doc += prize

    # 下乡医生奖金
    rest_results = []
    sum_rest_doc = 0
    for rdoc in rest_docs:
        prize = rdoc["奖金"] + 11
        rest_results.append({"姓名": rdoc["姓名"], "奖金": prize})
        sum_rest_doc += prize

    # 新职工奖金
    new_results = []
    sum_new_doc = 0
    for ndoc in new_docs:
        prize = ndoc["奖金"] + 11
        new_results.append({"姓名": ndoc["姓名"], "奖金": prize})
        sum_new_doc += prize

    # 主任医师奖金（固定每人同样奖金）
    dir_results = []
    sum_dir_doc = 0
    for ddoc in dir_docs:
        dir_results.append({"姓名": ddoc["姓名"], "奖金": cheng_tot + 11})
        sum_dir_doc += cheng_tot + 11

    # 李珊珊奖金
    lishanshan = hospital_pingjun + 2000 + 11

    # 实发奖金总数
    shifa = sum_doc + sum_new_doc + sum_rest_doc + sum_dir_doc + 600 + lishanshan + jiangli

    # 汇总所有奖金详情表
    all_results = normal_results + rest_results + new_results + dir_results
    df_all = pd.DataFrame(all_results)

    return df_all, {
        "工作量奖励": jiangli,
        "老总和教学秘书等补贴": 600,
        "李珊珊奖金": lishanshan,
        "主任医师奖金总计": sum_dir_doc,
        "普通医生奖金总计": sum_doc,
        "下乡医生奖金总计": sum_rest_doc,
        "新职工奖金总计": sum_new_doc,
        "奖金实发总数": shifa
    }


# 主界面分步流程控制
if "page" not in st.session_state:
    st.session_state.page = "input_basic"

# 默认主任医师列表（你原代码只有程伟波主任）
if "dir_docs" not in st.session_state:
    st.session_state.dir_docs = [{"姓名": "程伟波", "报告数": 0, "工作量": 0}]

if st.session_state.page == "input_basic":
    st.title("奖金分配工具 - 基本参数输入")

    st.write("请填写效益和床边相关参数（支持小数）:")

    xiaoyi_1 = st.number_input("效益1", value=10000.0)
    xiaoyi_2 = st.number_input("效益2", value=5000.0)
    fubu = st.number_input("腹部床边", value=1000.0)
    xinzang = st.number_input("心脏床边", value=1000.0)
    chanke = st.number_input("产科床边", value=1000.0)
    hospital_pingjun = st.number_input("院平均奖", value=5000.0)

    if st.button("下一步，输入普通医生信息"):
        # 保存参数
        st.session_state.xiaoyi_1 = xiaoyi_1
        st.session_state.xiaoyi_2 = xiaoyi_2
        st.session_state.fubu = fubu
        st.session_state.xinzang = xinzang
        st.session_state.chanke = chanke
        st.session_state.hospital_pingjun = hospital_pingjun
        st.session_state.docs = []
        st.session_state.rest_docs = []
        st.session_state.new_docs = []
        st.session_state.page = "input_doctors"

elif st.session_state.page == "input_doctors":
    st.title("输入普通医生信息")

    with st.form("doctor_form", clear_on_submit=True):
        name = st.text_input("姓名")
        report_num = st.number_input("报告数", min_value=0)
        workload = st.number_input("工作量", min_value=0)
        fubu_num = st.number_input("腹部床边", min_value=0)
        xinzang_num = st.number_input("心脏床边", min_value=0)
        chanke_num = st.number_input("产科床边", min_value=0)

        submitted = st.form_submit_button("添加普通医生")
        if submitted:
            st.session_state.docs.append({
                "姓名": name,
                "报告数": report_num,
                "工作量": workload,
                "腹部": fubu_num,
                "心脏": xinzang_num,
                "产科": chanke_num,
            })
            st.success(f"已添加医生：{name}")

    if st.button("查看普通医生列表"):
        if st.session_state.docs:
            st.table(pd.DataFrame(st.session_state.docs))
        else:
            st.info("暂无普通医生数据")

    if st.button("下一步，输入下乡进修产假医生奖金"):
        st.session_state.page = "input_rest_docs"

elif st.session_state.page == "input_rest_docs":
    st.title("输入下乡进修产假医生奖金")

    with st.form("rest_doc_form", clear_on_submit=True):
        name = st.text_input("姓名")
        bonus = st.number_input("奖金", min_value=0.0)

        submitted = st.form_submit_button("添加下乡进修医生")
        if submitted:
            st.session_state.rest_docs.append({
                "姓名": name,
                "奖金": bonus,
            })
            st.success(f"已添加下乡医生：{name}")

    if st.button("查看下乡进修医生列表"):
        if st.session_state.rest_docs:
            st.table(pd.DataFrame(st.session_state.rest_docs))
        else:
            st.info("暂无下乡进修医生数据")

    if st.button("下一步，输入新入职医生奖金"):
        st.session_state.page = "input_new_docs"

elif st.session_state.page == "input_new_docs":
    st.title("输入新入职医生奖金")

    with st.form("new_doc_form", clear_on_submit=True):
        name = st.text_input("姓名")
        multiplier = st.number_input("奖金倍率（平均奖倍数，1.0=平均奖）", min_value=0.0, value=1.0)

        submitted = st.form_submit_button("添加新入职医生")
        if submitted:
            bonus = multiplier * (st.session_state.xiaoyi_1 * 0.2 + st.session_state.xiaoyi_2 * 0.2)
            st.session_state.new_docs.append({
                "姓名": name,
                "奖金": bonus,
            })
            st.success(f"已添加新职工：{name}")

    if st.button("查看新入职医生列表"):
        if st.session_state.new_docs:
            st.table(pd.DataFrame(st.session_state.new_docs))
        else:
            st.info("暂无新职工数据")

    if st.button("下一步，计算奖金"):
        st.session_state.page = "show_result"

elif st.session_state.page == "show_result":
    st.title("奖金计算结果")

    df_all, summary = calculate_bonus(
        st.session_state.dir_docs,
        st.session_state.docs,
        st.session_state.rest_docs,
        st.session_state.new_docs,
        st.session_state.xiaoyi_1,
        st.session_state.xiaoyi_2,
        st.session_state.fubu,
        st.session_state.xinzang,
        st.session_state.chanke,
        st.session_state.hospital_pingjun,
    )

    st.subheader("奖金明细")
    st.table(df_all)

    st.subheader("奖金汇总")
    for k, v in summary.items():
        st.write(f"{k}：{v:.2f}")

    if st.button("重新开始"):
        keys = ["page", "docs", "rest_docs", "new_docs", "xiaoyi_1", "xiaoyi_2", "fubu",
                "xinzang", "chanke", "hospital_pingjun"]
        for key in keys:
            if key in st.session_state:
                del st.session_state[key]
        st.session_state.page = "input_basic"
