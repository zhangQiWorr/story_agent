import time
from datetime import datetime
import fitz
import os



def pdf_convert_images(pdf_file: str, dst_images_dir: str = "../images")  -> list[str]:

    file_name_prefix = os.path.splitext(os.path.basename(pdf_file))[0]

    pdf_document = fitz.open(pdf_file)
    dst_dir = f"{dst_images_dir}/{file_name_prefix}-{datetime.now().now()}"
    if not os.path.exists(dst_dir):
        os.makedirs(dst_dir)
    print(f"create dir {dst_dir}.")

    images_name= []
    for current_page in range(pdf_document.page_count):
        for img_index, img in enumerate(pdf_document.get_page_images(current_page)):
            xref = img[0]
            pix = fitz.Pixmap(pdf_document, xref)

            # 确保将图片转换为灰度图
            if pix.n > 3:  # 如果不是灰度或RGB，则已经是灰度或其他少于4个组件的形式
                pix_gray = fitz.Pixmap(fitz.csRGB, pix)

            image_path = f"{dst_dir}/page{current_page}-{img_index}.png"
            print(f"Processing page {current_page}, image {img_index}: {pix.width}x{pix.height}")
            pix_gray.save(image_path, jpg_quality=85)  # 注意：jpg_quality参数对于PNG格式不起作用

            images_name.append(image_path)

            # 释放Pixmap资源
            pix_gray = None
            pix = None
    return images_name

def pdf_convert_page_to_image(pdf_file: str, dst_images_dir: str = "../images") -> list[str]:
    """
    将PDF文件的每一页转换为单独的图片
    Args:
        pdf_file: PDF文件路径
        dst_images_dir: 输出图片目录
    Returns:
        list[str]: 生成的图片路径列表
    """
    file_name_prefix = os.path.splitext(os.path.basename(pdf_file))[0]
    
    pdf_document = fitz.open(pdf_file)
    dst_dir = f"{dst_images_dir}/{file_name_prefix}-{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    if not os.path.exists(dst_dir):
        os.makedirs(dst_dir)
    print(f"创建目录 {dst_dir}")

    images_name = []
    for page_num in range(pdf_document.page_count):
        page = pdf_document[page_num]
        # 设置缩放比例，可以根据需要调整
        zoom = 2
        mat = fitz.Matrix(zoom, zoom)
        pix = page.get_pixmap(matrix=mat)
        
        image_path = f"{dst_dir}/page_{page_num + 1}.png"
        print(f"处理第 {page_num + 1} 页: {pix.width}x{pix.height}")
        pix.save(image_path)
        
        images_name.append(image_path)
        pix = None  # 释放资源
    
    pdf_document.close()
    return images_name

# images_name = pdf_convert_page_to_image("../01- What a Mess-已压缩.pdf")
# print(images_name)

