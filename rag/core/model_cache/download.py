from huggingface_hub import snapshot_download

model_name = "BAAI/bge-small-zh-v1.5"
local_dir = "./bge-small-zh-v1.5"

print(f"开始下载模型：{model_name}")
print(f"保存目录：{local_dir}")

snapshot_download(
    repo_id=model_name,
    local_dir=local_dir,
    local_dir_use_symlinks=False,   # 使用真实文件（避免复制不完整）
)

print("下载完成！模型已保存到：", local_dir)
