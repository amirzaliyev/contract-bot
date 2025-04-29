import pandas as pd
from docx import Document
import os

def fill_template(template_path, output_path, context):
    doc = Document(template_path)

    for paragraph in doc.paragraphs:
        for key, value in context.items():
            if f"{{{{{key}}}}}" in paragraph.text:
                paragraph.text = paragraph.text.replace(f"{{{{{key}}}}}", str(value))

    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                for key, value in context.items():
                    if f"{{{{{key}}}}}" in cell.text:
                        cell.text = cell.text.replace(f"{{{{{key}}}}}", str(value))

    doc.save(output_path)

# # === Step 1: Load data from Excel ===
# excel_path = "clients.xlsx"  # <-- update this to your actual Excel file name
# df = pd.read_excel(excel_path)

# # === Step 2: Setup templates and output folder ===
# template1 = "template1.docx"
# template2 = "template2.docx"
# output_folder_c = "shartnomalar"
# output_folder_o = "buyruqlar"
# os.makedirs(output_folder_c, exist_ok=True)
# os.makedirs(output_folder_o, exist_ok=True)

# # === Step 3: Generate documents for each row ===
# for index, row in df.iterrows():
#     context = row.to_dict()

#     name_for_file = context["full_name"].replace(" ", "_")
#     print(context)
#     doc_id = context["document_id"]

#     output_path1 = os.path.join(output_folder_c, f"Mehnat_Shartnoma_{name_for_file}.docx")
#     output_path2 = os.path.join(output_folder_o, f"Buyruq SHT-{'0' if doc_id - 1 < 10 else ''}{doc_id - 1}.docx")

#     fill_template(template1, output_path1, context)
#     fill_template(template2, output_path2, context)

# print("All documents generated successfully.")
