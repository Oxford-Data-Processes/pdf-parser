TO DO:

- Create automated template builder
- Auto generate project documentation
- Build brew dependecies list


For template builder, run through OCR and Extraction and compare the words, see what % match. Use a threshold to classify as extraction or ocr method.

Only convert to jpg if the OCR method is used or if there is a max pixel value for lines.

Provide jpeg bytes in the pdf_data object for the OCR method.