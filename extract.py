import docx

doc = docx.Document('docs/Strategic Talent Intelligence Report_ The Angular Engineering Ecosystem and Automated Sourcing Architectures in India and Global Remote Markets.docx')
for p in doc.paragraphs:
    if '"name":' in p.text:
        print(p.text)
