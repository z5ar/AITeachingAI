try:
    from PIL import Image
    PIL_AVAILABLE = True
except Exception:
    Image = None
    PIL_AVAILABLE = False
from random import randint

def wcag(
    colour_a: tuple[int, int, int],
    colour_b: tuple[int, int, int]      
):
    colour_a = tuple(x/255 for x in colour_a)
    colour_b = tuple(x/255 for x in colour_b)
    linearise = lambda x: x/12.92 if x<=0.03928 else ((x+0.055)/1.055)**2.4
    colour_a = tuple(linearise(x) for x in colour_a)
    colour_b = tuple(linearise(x) for x in colour_b)
    wsum = lambda x: 0.2126*x[0] + 0.7152*x[1] + 0.0722*x[2]
    la = wsum(colour_a)
    lb = wsum(colour_b)
    if la<lb :
        la, lb = lb, la
    return (la+0.05)/(lb+0.05)

def get_identicon(username: str, output_path: str) -> bool:
    """Generate a tiny identicon for username.
    Returns True on success. If Pillow isn't available, returns False gracefully.
    """
    if not PIL_AVAILABLE:
        # Pillow not installed; skip generating to avoid crashing the app
        return False
    output = Image.new('RGB', (7,7), (240, 240, 240))
    i, hash_number, r, g, b = 0, 0, 0, 0, 0
    while True:
        hash_number = hash(f'{username}{i}')
        r, b = divmod(hash_number, 255)
        r, g = divmod(r, 255)
        r %= 255
        i += 1 
        if wcag((r, g, b), (240, 240, 240)) >= 1.2:
            break
    
    bhash = '111001011001011' + bin(hash_number)[2:]
    
    for x in range(3):
        for y in range(5):
            if bhash[-(x*5+y+1)] == '1':
                output.putpixel((x+1, y+1), (r, g, b))
                output.putpixel((5-x, y+1), (r, g, b))

    output.save(
        output_path, 
        'WEBP', 
        lossless=True,    # 无损保持质量
        method=6,         # 最高压缩比
        quality=100
    )      # 最高质量
    return True


if __name__ == '__main__':
    print(wcag((255,255,204), (240,240,240)))
    get_identicon('z5ar', '1.webp')