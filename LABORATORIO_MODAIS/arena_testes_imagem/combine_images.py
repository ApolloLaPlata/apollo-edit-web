
from PIL import Image

i3 = Image.open("LABORATORIO_MODAIS/arena_testes_imagem/char3_turnaround.png")
i4 = Image.open("LABORATORIO_MODAIS/arena_testes_imagem/char4_turnaround.png")

new_width = i3.width + i4.width
new_height = max(i3.height, i4.height)
new_im = Image.new("RGBA", (new_width, new_height))
new_im.paste(i3, (0,0))
new_im.paste(i4, (i3.width, 0))

new_im.save("LABORATORIO_MODAIS/arena_testes_imagem/char3_4_combined.png")

