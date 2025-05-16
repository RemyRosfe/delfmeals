import fitz
from pathlib import Path

# Vos chemins
pdfs_folder = r"C:\Users\Laura\Desktop\delfmeals\recettes_pdf"
images_folder = r"C:\Users\Laura\Desktop\delfmeals\recettes_images"

# Créer le dossier de sortie
Path(images_folder).mkdir(exist_ok=True)

# Trouver tous les PDFs
pdf_files = list(Path(pdfs_folder).glob("*.pdf"))
print(f"Trouvé {len(pdf_files)} fichiers PDF")

# Convertir chaque PDF
for i, pdf_file in enumerate(pdf_files, 1):
    print(f"\n[{i}/{len(pdf_files)}] {pdf_file.name}")
    
    # Créer un dossier pour ce PDF
    pdf_name = pdf_file.stem
    output_dir = Path(images_folder) / pdf_name
    output_dir.mkdir(exist_ok=True)
    
    # Utiliser un context manager pour être sûr de fermer le document
    try:
        with fitz.open(str(pdf_file)) as doc:
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
                pix.save(str(output_dir / f"page_{page_num+1:03d}.png"))
                print(f"  ✓ Page {page_num+1}")
            
            print(f"  ✅ {len(doc)} pages converties")
            
    except Exception as e:
        print(f"  ❌ Erreur avec {pdf_file.name}: {e}")

print("\n🍳 Conversion terminée !")
