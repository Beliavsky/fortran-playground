"""Runtime image previews; keep conversion out of compiled-library recipes."""
import base64
from io import BytesIO
import os
from pathlib import Path
import stat

import fortran_plot as png

PNM_SUFFIXES = {'.pnm', '.pbm', '.pgm', '.ppm'}
MAX_PNM_BYTES = 16 * 1024 * 1024


def snapshot(directory):
    values = png.snapshot(directory)
    with os.scandir(directory) as entries:
        for index, entry in enumerate(entries):
            if index >= 10000:
                break
            if Path(entry.name).suffix.lower() in PNM_SUFFIXES and entry.is_file(follow_symlinks=False):
                # DirEntry.stat() can report inode=0 on Windows, unlike fstat.
                info = Path(entry.path).lstat()
                values[entry.name] = (info.st_mtime_ns, info.st_size, info.st_ino)
    return values


def pnm_to_png(data):
    # Import only when a program actually produces a PNM image. Matplotlib's
    # existing hosted installation already includes Pillow.
    if len(data) > MAX_PNM_BYTES or data[:2] not in {b'P1', b'P2', b'P3', b'P4', b'P5', b'P6'}:
        raise ValueError('Invalid or oversized PNM image')
    from PIL import Image
    try:
        with Image.open(BytesIO(data), formats=['PPM']) as original:
            width, height = original.size
            if not (0 < width <= 4096 and 0 < height <= 4096 and width * height <= 8000000):
                raise ValueError('PNM image dimensions exceed preview limits')
            original.load()
            with original.convert('RGB') as image:
                output = BytesIO()
                image.save(output, format='PNG')
    except Image.DecompressionBombError as error:
        raise ValueError('PNM image dimensions exceed preview limits') from error
    result = output.getvalue()
    if len(result) > png.MAX_PNG_BYTES or not png.valid_png(result):
        raise ValueError('Converted image exceeds PNG preview limits')
    return result


def collect_plots(directory, before=None):
    before = before or {}
    result = png.collect_plots(directory, before)
    plots, notes = result['plots'], result['plot_notes']
    total = sum(len(base64.b64decode(p['data'])) for p in plots)
    for name, identity in sorted(snapshot(directory).items()):
        if Path(name).suffix.lower() not in PNM_SUFFIXES or before.get(name) == identity:
            continue
        if len(plots) >= png.MAX_PLOTS:
            notes.append('Additional image omitted (four previews / 1 MiB total limit).')
            break
        if identity[1] > MAX_PNM_BYTES:
            notes.append(f'{name}: PNM input exceeds the 16 MiB limit.')
            continue
        descriptor = None
        try:
            descriptor = os.open(Path(directory) / name, os.O_RDONLY | getattr(os, 'O_NOFOLLOW', 0)
                                 | getattr(os, 'O_NONBLOCK', 0) | getattr(os, 'O_BINARY', 0))
            info = os.fstat(descriptor)
            if not stat.S_ISREG(info.st_mode) or (info.st_mtime_ns, info.st_size, info.st_ino) != identity:
                continue
            with os.fdopen(descriptor, 'rb') as stream:
                descriptor = None
                data = stream.read(MAX_PNM_BYTES + 1)
            converted = pnm_to_png(data)
            if len(converted) > png.MAX_PNG_BYTES - total:
                notes.append(f'{name}: converted image exceeds the aggregate preview limit.')
                continue
            plots.append({'name': name + ' (PNG preview)', 'mime': 'image/png',
                          'data': base64.b64encode(converted).decode('ascii')})
            total += len(converted)
        except ImportError:
            notes.append(f'{name}: install Pillow to preview PNM images locally.')
        except (OSError, ValueError, SyntaxError, OverflowError):
            notes.append(f'{name}: invalid or unsupported PNM image omitted.')
        finally:
            if descriptor is not None:
                os.close(descriptor)
    result['plot_notes'] = list(dict.fromkeys(notes))
    return result
