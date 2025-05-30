import argparse
from pathlib import Path

def merge_m3u_files(input_files, output_file):
    """
    合併多個 M3U 文件到一個輸出文件中
    
    :param input_files: 要合併的 M3U 文件路徑列表
    :param output_file: 合併後的輸出文件路徑
    """
    unique_entries = set()
    
    # 讀取所有輸入文件
    for file_path in input_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and line not in unique_entries:
                        unique_entries.add(line)
        except Exception as e:
            print(f"無法讀取文件 {file_path}: {e}")
    
    # 寫入輸出文件
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("#EXTM3U\n")  # 寫入 M3U 頭部
            for entry in sorted(unique_entries):
                f.write(f"{entry}\n")
        print(f"成功合併 {len(input_files)} 個文件到 {output_file}，共 {len(unique_entries)} 個唯一條目。")
    except Exception as e:
        print(f"無法寫入輸出文件 {output_file}: {e}")

def main():
    # 設置命令行參數
    parser = argparse.ArgumentParser(description='合併多個 M3U 文件')
    parser.add_argument('-i', '--input', nargs='+', required=True, help='要合併的 M3U 文件列表')
    parser.add_argument('-o', '--output', required=True, help='合併後的輸出文件路徑')
    
    args = parser.parse_args()
    
    # 檢查輸入文件是否存在
    input_files = []
    for file_path in args.input:
        path = Path(file_path)
        if not path.exists():
            print(f"警告: 文件 {file_path} 不存在，將跳過")
        else:
            input_files.append(file_path)
    
    if not input_files:
        print("錯誤: 沒有有效的輸入文件")
        return
    
    # 執行合併
    merge_m3u_files(input_files, args.output)

if __name__ == '__main__':
    main()