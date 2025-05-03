import argparse
import os
from head_stabilizer import HeadStabilizer
from head_alignment_viewer import HeadAlignmentViewer

def main():
    """主函数 - 处理命令行参数并启动应用程序"""
    # 创建命令行参数解析器
    parser = argparse.ArgumentParser(description="头部对齐工具 - 对多张照片中的人脸进行精确对齐")
    parser.add_argument("--folder", "-f", type=str, help="要处理的图片文件夹路径")
    parser.add_argument("--reference", "-r", type=str, help="参考图片路径（强烈推荐提供）")
    parser.add_argument("--debug", "-d", action="store_true", help="启用调试模式，显示面部关键点")
    parser.add_argument("--size", "-s", type=int, nargs=2, default=[512, 512], help="默认输出图像尺寸，例如: 512 512 (如提供参考图片则使用参考图片尺寸)")
    parser.add_argument("--keep-background", "-k", action="store_true", help="保留背景（不推荐，可能导致尺寸不一致）")
    
    args = parser.parse_args()
    
    # 如果没有提供文件夹参数，使用默认值
    folder_path = args.folder if args.folder else "/Users/loneranger/Project/DeforumAI/瞬息宇宙"
    
    print(f"======== 头部对齐工具 ========")
    print(f"处理文件夹: {folder_path}")
    
    # 检查是否提供了参考图片
    if not args.reference:
        print(f"警告: 未通过命令行提供参考图片，将在界面中要求选择")
    else:
        print(f"参考图片: {args.reference}")
    
    print(f"调试模式: {'开启' if args.debug else '关闭'}")
    print(f"默认输出尺寸: {args.size[0]}x{args.size[1]}")
    print(f"保留背景: {'是' if args.keep_background else '否（推荐）'}")
    print(f"==============================")
    
    try:
        # 创建查看器实例
        viewer = HeadAlignmentViewer(folder_path, output_size=(args.size[0], args.size[1]))
        
        # 设置初始参数
        if args.debug:
            viewer.debug_mode.set(1)
            viewer.stabilizer.debug = True
        
        if args.keep_background:
            viewer.preserve_bg.set(1)
            viewer.stabilizer.preserve_background = True
        else:
            viewer.preserve_bg.set(0)
            viewer.stabilizer.preserve_background = False
        
        # 如果提供了参考图片，设置参考图片路径
        if args.reference:
            viewer.reference_image_path = args.reference
            viewer.ref_image_label.config(text=f"已选择: {os.path.basename(args.reference)}", fg="green")
        
        # 启动查看器
        viewer.run()
    except Exception as e:
        print(f"程序启动错误: {e}")
        import traceback
        traceback.print_exc()
        input("按Enter键退出...")

if __name__ == "__main__":
    main()