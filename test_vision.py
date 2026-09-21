import modal
import base64
import asyncio

async def test():
    engine = modal.Cls.lookup("apollo-vision-engine", "FlorenceVisionEngine")
    
    # fake 1x1 image
    fake_img = b"iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNk+A8AAQUBAScY42YAAAAASUVORK5CYII="
    
    res = await engine().analyze_image.remote.aio(fake_img.decode("utf-8"))
    print("Result:", res)

if __name__ == "__main__":
    asyncio.run(test())
