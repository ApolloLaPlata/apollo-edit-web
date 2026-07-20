import re

filepath = r'E:\MEUS PROGRAMAS\APOLLO_STUDIO\web_ui\noticias_core.js'
with open(filepath, 'r', encoding='latin-1') as f:
    content = f.read()

target1 = """<i class="fas fa-pen-tool"></i> Usar
                            </button>"""
replace1 = """<i class="fas fa-pen-tool"></i> Usar
                            </button>
                            <button id="btn-deepdive-${idx}" onclick="newsDeepDive(${idx})" style="padding: 8px 12px; background: #8b5cf6; color: white; border: none; border-radius: 6px; cursor: pointer; transition: background 0.2s;" onmouseover="this.style.background='#7c3aed'" onmouseout="this.style.background='#8b5cf6'" title="Aprofundar Notícia">
                                <i class="fas fa-search-plus"></i>
                            </button>"""

target2 = """<i class="fas fa-external-link-alt"></i>
                            </a>
                        </div>
                    </div>"""
replace2 = """<i class="fas fa-external-link-alt"></i>
                            </a>
                        </div>
                        <div id="deep-dive-${idx}" style="display: none;"></div>
                    </div>"""

if "btn-deepdive-" not in content:
    content = content.replace(target1, replace1)
    content = content.replace(target2, replace2)
    with open(filepath, 'w', encoding='latin-1') as f:
        f.write(content)
    print("noticias_core.js patched!")
else:
    print("Already patched.")
