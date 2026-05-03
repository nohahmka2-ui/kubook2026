import streamlit as st
import easyocr
from pdf2image import convert_from_path
import numpy as np
from fpdf import FPDF
from arabic_reshaper import reshape
from bidi.algorithm import get_display
import tempfile

# إعداد واجهة الموقع
st.set_page_config(page_title="نظام الكتب الرسمية", layout="centered")
st.title("📄 محول الكتب الرسمية (سكان)")

st.info("ارفع ملف الـ PDF الممسوح ضوئياً (Scan) وسنقوم بتعبئة الفورمة تلقائياً.")

uploaded_file = st.file_uploader("اختر ملف PDF", type="pdf")

if uploaded_file:
    with st.spinner('جاري معالجة الصور وقراءة النص العربي...'):
        # حفظ الملف المرفوع مؤقتاً لقراءته
        with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
            tmp_file.write(uploaded_file.read())
            
        # تحويل الـ PDF لصور (تحتاج مكتبة poppler)
        images = convert_from_path(tmp_file.name)
        
        # تشغيل قارئ النصوص الذكي
        reader = easyocr.Reader(['ar'])
        all_text = ""
        for img in images:
            results = reader.readtext(np.array(img), detail=0)
            all_text += " ".join(results) + " "

    st.subheader("البيانات المستخرجة (يمكنك التعديل عليها)")
    
    # محاولة استخراج التاريخ ورقم الصادر بشكل تلقائي بسيط
    # هنا تضع البيانات في خانات ليقوم المستخدم بالتأكد منها
    col1, col2 = st.columns(2)
    with col1:
        subject = st.text_area("الموضوع:", value="بخصوص موضوع المعاملة المرفقة")
        ref_num = st.text_input("رقم الصادر:", value="123/2026")
    with col2:
        doc_date = st.text_input("التاريخ:", value="2026/05/03")

    if st.button("إصدار كتاب PDF الرسمي"):
        # إنشاء الـ PDF الجديد بالفورمة المطلوبة
        pdf = FPDF()
        pdf.add_page()
        
        # ملاحظة: ستحتاج لرفع خط عربي مع الملفات في GitHub ليظهر النص
        # سنستخدم هنا نصاً بسيطاً (يفضل تحميل خط Arial.ttf)
        
        def format_ar(text):
            return get_display(reshape(text))

        pdf.set_font("Arial", size=14)
        
        text_content = [
            f"الموضوع: {subject}",
            "",
            "يهديكم مكتب مساعد نائب مدير الجامعة للخدمات الأكاديمية المساندة لتقنية المعلومات أطيب التحيات،",
            f"بالإشارة إلى كتاب صادر رقم ({ref_num}) بتاريخ {doc_date} بخصوص الموضوع أعلاه.",
            "",
            "نرفق لعنايتكم كتاب بشأن الموضوع المذكور أعلاه، الرجاء التكرم بالعلم والإحاطة واتخاذ ما يلزم.",
            "",
            "وتفضلوا بقبول فائق الاحترام والتقدير،،",
            "",
            "المرفقات: أصل الكتاب المرفق"
        ]

        for line in text_content:
            pdf.multi_cell(0, 10, txt=format_ar(line), align='R')
            
        pdf_output = pdf.output(dest='S').encode('latin-1')
        st.download_button("⬇️ تحميل الكتاب الجديد", data=pdf_output, file_name="official_letter.pdf")