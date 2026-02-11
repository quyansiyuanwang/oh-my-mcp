"""
Compression tool handlers.

Provides tools for:
- ZIP compression and extraction
- TAR compression and extraction
- Archive content listing
"""

import json
import zipfile
import tarfile
from typing import List

from mcp_server.tools.registry import tool_handler
from mcp_server.utils import (
    logger,
    ValidationError,
    FileOperationError,
    sanitize_path,
    safe_get_file_size,
    format_bytes,
    validate_archive_safety,
)


@tool_handler
def compress_zip(files: List[str], output_path: str, compression_level: int = 6) -> str:
    """
    Create a ZIP archive from files.

    Args:
        files: List of file paths to compress
        output_path: Path for output ZIP file
        compression_level: Compression level 0-9 (default: 6)

    Returns:
        JSON string with archive info (path, size, compression ratio)
    """
    try:
        # 验证输入
        if not files:
            raise ValidationError("File list cannot be empty")

        if not isinstance(files, list):
            raise ValidationError("Files must be a list")

        if not 0 <= compression_level <= 9:
            raise ValidationError("Compression level must be 0-9")

        # 验证所有文件存在
        total_size = 0
        validated_files = []
        for file_path in files:
            p = sanitize_path(file_path)
            if not p.exists():
                raise FileOperationError(f"File not found: {file_path}")
            if not p.is_file():
                raise FileOperationError(f"Not a file: {file_path}")
            total_size += safe_get_file_size(p)
            validated_files.append(p)

        # 创建 ZIP
        output = sanitize_path(output_path)
        output.parent.mkdir(parents=True, exist_ok=True)

        with zipfile.ZipFile(
            output, "w", zipfile.ZIP_DEFLATED, compresslevel=compression_level
        ) as zf:
            for p in validated_files:
                zf.write(p, p.name)

        # 计算压缩率
        compressed_size = safe_get_file_size(output)
        ratio = (1 - compressed_size / total_size) * 100 if total_size > 0 else 0

        logger.info(
            f"Created ZIP archive: {output} ({len(validated_files)} files, "
            f"{format_bytes(compressed_size)})"
        )

        return json.dumps(
            {
                "success": True,
                "archive_path": str(output),
                "original_size": format_bytes(total_size),
                "compressed_size": format_bytes(compressed_size),
                "compression_ratio": f"{ratio:.1f}%",
                "file_count": len(validated_files),
            }
        )

    except (ValidationError, FileOperationError) as e:
        logger.error(f"ZIP compression failed: {e}")
        return json.dumps({"error": str(e), "type": "validation"})
    except Exception as e:
        logger.error(f"Unexpected error in compress_zip: {e}")
        return json.dumps({"error": str(e), "type": "unknown"})


@tool_handler
def extract_zip(zip_path: str, extract_to: str = ".", password: str = None) -> str:
    """
    Extract a ZIP archive.

    Args:
        zip_path: Path to ZIP file
        extract_to: Directory to extract to (default: current directory)
        password: Optional password for encrypted ZIP

    Returns:
        JSON string with extracted file list and total size
    """
    try:
        # 验证输入
        zip_file = sanitize_path(zip_path)
        if not zip_file.exists():
            raise FileOperationError(f"ZIP file not found: {zip_path}")
        if not zip_file.is_file():
            raise FileOperationError(f"Not a file: {zip_path}")

        # 验证安全性（防止 ZIP bomb）
        validate_archive_safety(zip_file)

        # 准备解压目录
        extract_dir = sanitize_path(extract_to)
        extract_dir.mkdir(parents=True, exist_ok=True)

        # 解压文件
        extracted_files = []
        total_size = 0

        pwd_bytes = password.encode("utf-8") if password else None

        with zipfile.ZipFile(zip_file, "r") as zf:
            for member in zf.namelist():
                # 安全检查：防止路径遍历
                member_path = extract_dir / member
                try:
                    member_path.resolve().relative_to(extract_dir.resolve())
                except ValueError:
                    raise ValidationError(
                        f"Unsafe path in archive: {member} (path traversal attempt)"
                    )

                # 解压文件
                zf.extract(member, extract_dir, pwd=pwd_bytes)
                extracted_files.append(member)

                # 计算大小
                file_info = zf.getinfo(member)
                total_size += file_info.file_size

        logger.info(
            f"Extracted ZIP archive: {zip_file} ({len(extracted_files)} files, "
            f"{format_bytes(total_size)})"
        )

        return json.dumps(
            {
                "success": True,
                "extracted_files": extracted_files,
                "file_count": len(extracted_files),
                "total_size": format_bytes(total_size),
                "extract_directory": str(extract_dir),
            }
        )

    except (ValidationError, FileOperationError) as e:
        logger.error(f"ZIP extraction failed: {e}")
        return json.dumps({"error": str(e), "type": "validation"})
    except zipfile.BadZipFile as e:
        logger.error(f"Invalid ZIP file: {e}")
        return json.dumps({"error": f"Invalid ZIP file: {e}", "type": "file"})
    except RuntimeError as e:
        # 密码错误或加密问题
        logger.error(f"ZIP extraction error: {e}")
        return json.dumps({"error": f"Extraction failed (check password): {e}", "type": "file"})
    except Exception as e:
        logger.error(f"Unexpected error in extract_zip: {e}")
        return json.dumps({"error": str(e), "type": "unknown"})


@tool_handler
def compress_tar(files: List[str], output_path: str, compression: str = "gz") -> str:
    """
    Create a TAR archive from files.

    Args:
        files: List of file paths to compress
        output_path: Path for output TAR file
        compression: Compression type - "none", "gz", or "bz2" (default: "gz")

    Returns:
        JSON string with archive info
    """
    try:
        # 验证输入
        if not files:
            raise ValidationError("File list cannot be empty")

        if not isinstance(files, list):
            raise ValidationError("Files must be a list")

        if compression not in ["none", "gz", "bz2"]:
            raise ValidationError("Compression must be 'none', 'gz', or 'bz2'")

        # 验证所有文件存在
        total_size = 0
        validated_files = []
        for file_path in files:
            p = sanitize_path(file_path)
            if not p.exists():
                raise FileOperationError(f"File not found: {file_path}")
            if not p.is_file():
                raise FileOperationError(f"Not a file: {file_path}")
            total_size += safe_get_file_size(p)
            validated_files.append(p)

        # 创建 TAR
        output = sanitize_path(output_path)
        output.parent.mkdir(parents=True, exist_ok=True)

        # 确定压缩模式
        mode_map = {"none": "w", "gz": "w:gz", "bz2": "w:bz2"}
        mode = mode_map[compression]

        with tarfile.open(output, mode) as tf:
            for p in validated_files:
                tf.add(p, arcname=p.name)

        # 计算压缩率
        compressed_size = safe_get_file_size(output)
        ratio = (1 - compressed_size / total_size) * 100 if total_size > 0 else 0

        logger.info(
            f"Created TAR archive: {output} ({len(validated_files)} files, "
            f"{format_bytes(compressed_size)})"
        )

        return json.dumps(
            {
                "success": True,
                "archive_path": str(output),
                "original_size": format_bytes(total_size),
                "compressed_size": format_bytes(compressed_size),
                "compression_ratio": f"{ratio:.1f}%",
                "compression_type": compression,
                "file_count": len(validated_files),
            }
        )

    except (ValidationError, FileOperationError) as e:
        logger.error(f"TAR compression failed: {e}")
        return json.dumps({"error": str(e), "type": "validation"})
    except Exception as e:
        logger.error(f"Unexpected error in compress_tar: {e}")
        return json.dumps({"error": str(e), "type": "unknown"})


@tool_handler
def extract_tar(tar_path: str, extract_to: str = ".") -> str:
    """
    Extract a TAR archive.

    Args:
        tar_path: Path to TAR file
        extract_to: Directory to extract to (default: current directory)

    Returns:
        JSON string with extracted file list
    """
    try:
        # 验证输入
        tar_file = sanitize_path(tar_path)
        if not tar_file.exists():
            raise FileOperationError(f"TAR file not found: {tar_path}")
        if not tar_file.is_file():
            raise FileOperationError(f"Not a file: {tar_path}")

        # 验证安全性
        validate_archive_safety(tar_file)

        # 准备解压目录
        extract_dir = sanitize_path(extract_to)
        extract_dir.mkdir(parents=True, exist_ok=True)

        # 解压文件
        extracted_files = []
        total_size = 0

        with tarfile.open(tar_file, "r:*") as tf:
            for member in tf.getmembers():
                # 安全检查：防止路径遍历
                member_path = extract_dir / member.name
                try:
                    member_path.resolve().relative_to(extract_dir.resolve())
                except ValueError:
                    raise ValidationError(
                        f"Unsafe path in archive: {member.name} (path traversal attempt)"
                    )

                # 解压
                tf.extract(member, extract_dir)
                extracted_files.append(member.name)
                total_size += member.size

        logger.info(
            f"Extracted TAR archive: {tar_file} ({len(extracted_files)} files, "
            f"{format_bytes(total_size)})"
        )

        return json.dumps(
            {
                "success": True,
                "extracted_files": extracted_files,
                "file_count": len(extracted_files),
                "total_size": format_bytes(total_size),
                "extract_directory": str(extract_dir),
            }
        )

    except (ValidationError, FileOperationError) as e:
        logger.error(f"TAR extraction failed: {e}")
        return json.dumps({"error": str(e), "type": "validation"})
    except tarfile.TarError as e:
        logger.error(f"Invalid TAR file: {e}")
        return json.dumps({"error": f"Invalid TAR file: {e}", "type": "file"})
    except Exception as e:
        logger.error(f"Unexpected error in extract_tar: {e}")
        return json.dumps({"error": str(e), "type": "unknown"})


@tool_handler
def list_archive_contents(archive_path: str) -> str:
    """
    List contents of an archive file without extracting.

    Args:
        archive_path: Path to archive file (ZIP, TAR, TAR.GZ, TAR.BZ2)

    Returns:
        JSON string with file list, sizes, and modification times
    """
    try:
        # 验证输入
        archive_file = sanitize_path(archive_path)
        if not archive_file.exists():
            raise FileOperationError(f"Archive file not found: {archive_path}")
        if not archive_file.is_file():
            raise FileOperationError(f"Not a file: {archive_path}")

        file_ext = archive_file.suffix.lower()
        files_info = []
        total_size = 0
        total_compressed = 0

        if file_ext == ".zip":
            with zipfile.ZipFile(archive_file, "r") as zf:
                for info in zf.infolist():
                    if not info.is_dir():
                        files_info.append(
                            {
                                "name": info.filename,
                                "size": format_bytes(info.file_size),
                                "compressed_size": format_bytes(info.compress_size),
                                "modified": info.date_time,
                            }
                        )
                        total_size += info.file_size
                        total_compressed += info.compress_size

        elif file_ext in [".tar", ".gz", ".bz2", ".tgz", ".tbz2"]:
            with tarfile.open(archive_file, "r:*") as tf:
                for member in tf.getmembers():
                    if member.isfile():
                        files_info.append(
                            {
                                "name": member.name,
                                "size": format_bytes(member.size),
                                "modified": member.mtime,
                            }
                        )
                        total_size += member.size
                total_compressed = safe_get_file_size(archive_file)

        else:
            raise ValidationError(
                f"Unsupported archive format: {file_ext}. "
                "Supported: .zip, .tar, .gz, .bz2, .tgz, .tbz2"
            )

        compression_ratio = (1 - total_compressed / total_size) * 100 if total_size > 0 else 0

        logger.info(f"Listed archive contents: {archive_file} ({len(files_info)} files)")

        return json.dumps(
            {
                "success": True,
                "archive_path": str(archive_file),
                "archive_type": file_ext,
                "file_count": len(files_info),
                "total_size": format_bytes(total_size),
                "compressed_size": format_bytes(total_compressed),
                "compression_ratio": f"{compression_ratio:.1f}%",
                "files": files_info,
            }
        )

    except (ValidationError, FileOperationError) as e:
        logger.error(f"Failed to list archive contents: {e}")
        return json.dumps({"error": str(e), "type": "validation"})
    except (zipfile.BadZipFile, tarfile.TarError) as e:
        logger.error(f"Invalid archive file: {e}")
        return json.dumps({"error": f"Invalid archive file: {e}", "type": "file"})
    except Exception as e:
        logger.error(f"Unexpected error in list_archive_contents: {e}")
        return json.dumps({"error": str(e), "type": "unknown"})
