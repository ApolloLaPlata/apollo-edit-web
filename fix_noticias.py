import io

filepath = 'web_ui/noticias_core.js'
content = io.open(filepath, 'r', encoding='utf-8').read()

# 1. card.innerHTML in renderSavedVideos (1202)
block1_old = """        card.innerHTML = \\
            <div style="position: relative; aspect-ratio: 16/9; background: #f3f4f6;">
                <img src="\\" alt="" style="width: 100%; height: 100%; object-fit: cover;">
                <div style="position: absolute; bottom: 8px; right: 8px; background: rgba(0,0,0,0.8); color: white; font-size: 12px; font-weight: 700; padding: 2px 6px; border-radius: 4px; display: flex; align-items: center; gap: 4px;">
                    <i class="far fa-clock"></i> \\
                </div>
                <button onclick="handleToggleSaveVideo('\\')" title="Remover dos salvos" style="position: absolute; top: 8px; right: 8px; padding: 8px; border-radius: 50%; background: #dc2626; color: white; border: none; cursor: pointer; box-shadow: 0 1px 2px rgba(0,0,0,0.1);">
                    <i class="fas fa-bookmark"></i>
                </button>
            </div>
            <div style="padding: 16px; flex: 1; display: flex; flex-direction: column;">
                <h3 style="font-weight: 700; color: #111827; margin: 0 0 4px 0; font-size: 16px; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden;" title="\\">\\</h3>
                <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 12px; font-size: 12px; color: #6b7280;">
                    <span style="font-weight: 500; color: #374151;">\\</span>
                    <span></span>
                    <span>\\</span>
                </div>
                
                <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 8px; margin-bottom: 16px; font-size: 12px; color: #4b5563; background: #f9fafb; padding: 8px; border-radius: 8px; border: 1px solid #f3f4f6;">
                    <div style="display: flex; flex-direction: column; align-items: center; justify-content: center; text-align: center;" title="Visualizaes">
                        <i class="fas fa-desktop" style="margin-bottom: 4px; color: #9ca3af;"></i>
                        <span style="font-weight: 600; color: #374151;">\\</span>
                    </div>
                    <div style="display: flex; flex-direction: column; align-items: center; justify-content: center; text-align: center;" title="Curtidas (Estimativa)">
                        <i class="far fa-thumbs-up" style="margin-bottom: 4px; color: #9ca3af;"></i>
                        <span style="font-weight: 600; color: #374151;">\\</span>
                    </div>
                    <div style="display: flex; flex-direction: column; align-items: center; justify-content: center; text-align: center;" title="Comentrios (Estimativa)">
                        <i class="far fa-comment" style="margin-bottom: 4px; color: #9ca3af;"></i>
                        <span style="font-weight: 600; color: #374151;">\\</span>
                    </div>
                    <div style="display: flex; flex-direction: column; align-items: center; justify-content: center; text-align: center;" title="Compartilhamentos (Estimativa)">
                        <i class="fas fa-share-alt" style="margin-bottom: 4px; color: #9ca3af;"></i>
                        <span style="font-weight: 600; color: #374151;">\\</span>
                    </div>
                </div>

                <p style="font-size: 14px; color: #4b5563; margin-bottom: 16px; flex: 1; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden;">\\</p>
                
                <div style="margin-top: auto; padding-top: 16px; border-top: 1px solid #f3f4f6;">
                    <div style="display: flex; gap: 8px;">
                        <button onclick="analyzeSavedVideo('\\')" \\ style="flex: 1; background: #fef2f2; color: #b91c1c; padding: 8px; border-radius: 6px; border: none; font-size: 14px; font-weight: 500; cursor: pointer; display: flex; align-items: center; justify-content: center; gap: 4px; \\">
                            <i class="\\"></i> Analisar com IA
                        </button>
                        <button onclick="generateVideoScript('\\')" \\ style="flex: 1; background: #18181b; color: white; padding: 8px; border-radius: 6px; border: none; font-size: 14px; font-weight: 500; cursor: pointer; display: flex; align-items: center; justify-content: center; gap: 4px; \\">
                            <i class="\\"></i> Criar Roteiro
                        </button>
                        <button onclick="playVideo('\\')" style="padding: 8px 12px; background: #f9fafb; color: #4b5563; border: none; border-radius: 6px; cursor: pointer;" title="Assistir no App">
                            <i class="fas fa-external-link-alt"></i>
                        </button>
                    </div>
                    
                    \\
                </div>
            </div>
        \\;"""

block1_new = """        card.innerHTML = `
            <div style="position: relative; aspect-ratio: 16/9; background: #f3f4f6;">
                <img src="${video.thumbnail || ''}" alt="" style="width: 100%; height: 100%; object-fit: cover;">
                <div style="position: absolute; bottom: 8px; right: 8px; background: rgba(0,0,0,0.8); color: white; font-size: 12px; font-weight: 700; padding: 2px 6px; border-radius: 4px; display: flex; align-items: center; gap: 4px;">
                    <i class="far fa-clock"></i> ${video.duration || 'N/A'}
                </div>
                <button onclick="handleToggleSaveVideo('${video.url}')" title="Remover dos salvos" style="position: absolute; top: 8px; right: 8px; padding: 8px; border-radius: 50%; background: #dc2626; color: white; border: none; cursor: pointer; box-shadow: 0 1px 2px rgba(0,0,0,0.1);">
                    <i class="fas fa-bookmark"></i>
                </button>
            </div>
            <div style="padding: 16px; flex: 1; display: flex; flex-direction: column;">
                <h3 style="font-weight: 700; color: #111827; margin: 0 0 4px 0; font-size: 16px; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden;" title="${video.title}">${video.title}</h3>
                <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 12px; font-size: 12px; color: #6b7280;">
                    <span style="font-weight: 500; color: #374151;">${video.author || 'Desconhecido'}</span>
                    <span>•</span>
                    <span>${video.ago || 'N/A'}</span>
                </div>
                
                <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 8px; margin-bottom: 16px; font-size: 12px; color: #4b5563; background: #f9fafb; padding: 8px; border-radius: 8px; border: 1px solid #f3f4f6;">
                    <div style="display: flex; flex-direction: column; align-items: center; justify-content: center; text-align: center;" title="Visualizações">
                        <i class="fas fa-desktop" style="margin-bottom: 4px; color: #9ca3af;"></i>
                        <span style="font-weight: 600; color: #374151;">${formatNumber(video.views)}</span>
                    </div>
                    <div style="display: flex; flex-direction: column; align-items: center; justify-content: center; text-align: center;" title="Curtidas (Estimativa)">
                        <i class="far fa-thumbs-up" style="margin-bottom: 4px; color: #9ca3af;"></i>
                        <span style="font-weight: 600; color: #374151;">${formatNumber(video.likes)}</span>
                    </div>
                    <div style="display: flex; flex-direction: column; align-items: center; justify-content: center; text-align: center;" title="Comentários (Estimativa)">
                        <i class="far fa-comment" style="margin-bottom: 4px; color: #9ca3af;"></i>
                        <span style="font-weight: 600; color: #374151;">${formatNumber(video.comments)}</span>
                    </div>
                    <div style="display: flex; flex-direction: column; align-items: center; justify-content: center; text-align: center;" title="Compartilhamentos (Estimativa)">
                        <i class="fas fa-share-alt" style="margin-bottom: 4px; color: #9ca3af;"></i>
                        <span style="font-weight: 600; color: #374151;">${formatNumber(video.shares)}</span>
                    </div>
                </div>

                <p style="font-size: 14px; color: #4b5563; margin-bottom: 16px; flex: 1; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden;">${video.description || 'Sem descrição.'}</p>
                
                <div style="margin-top: auto; padding-top: 16px; border-top: 1px solid #f3f4f6;">
                    <div style="display: flex; gap: 8px;">
                        <button onclick="analyzeSavedVideo('${video.url}')" ${isAnalyzing ? 'disabled' : ''} style="flex: 1; background: #fef2f2; color: #b91c1c; padding: 8px; border-radius: 6px; border: none; font-size: 14px; font-weight: 500; cursor: pointer; display: flex; align-items: center; justify-content: center; gap: 4px; ${isAnalyzing ? 'opacity: 0.7;' : ''}">
                            <i class="${isAnalyzing ? 'fas fa-spinner fa-spin' : 'fas fa-robot'}"></i> Analisar com IA
                        </button>
                        <button onclick="generateVideoScript('${video.url}')" ${isGenerating ? 'disabled' : ''} style="flex: 1; background: #18181b; color: white; padding: 8px; border-radius: 6px; border: none; font-size: 14px; font-weight: 500; cursor: pointer; display: flex; align-items: center; justify-content: center; gap: 4px; ${isGenerating ? 'opacity: 0.7;' : ''}">
                            <i class="${isGenerating ? 'fas fa-spinner fa-spin' : 'fas fa-magic'}"></i> Criar Roteiro
                        </button>
                        <button onclick="playVideo('${video.url}')" style="padding: 8px 12px; background: #f9fafb; color: #4b5563; border: none; border-radius: 6px; cursor: pointer;" title="Assistir no App">
                            <i class="fas fa-external-link-alt"></i>
                        </button>
                    </div>
                    
                    ${analysisHtml}
                </div>
            </div>
        `;"""
content = content.replace(block1_old, block1_new)

# 2. iframe.src (1327)
content = content.replace("iframe.src = \\https://www.youtube.com/embed/\\?autoplay=1\\;", "iframe.src = `https://www.youtube.com/embed/${videoId}?autoplay=1`;")

# 3. recentVideos array (1386)
block3_old = """            recentVideos: Array.from({length: 20}).map((_, i) => ({
                title: \\Vdeo Viral Simulado \\ - Dicas e Estratgias\\,
                views: \\\\K\\,
                likes: \\\\K\\,
                date: \\H \\ dias\\
            }))"""
block3_new = """            recentVideos: Array.from({length: 20}).map((_, i) => ({
                title: `Vídeo Viral Simulado ${i + 1} - Dicas e Estratégias`,
                views: `${Math.floor(Math.random() * 900 + 100)}K`,
                likes: `${Math.floor(Math.random() * 90 + 10)}K`,
                date: `Há ${Math.floor(Math.random() * 5 + 1)} dias`
            }))"""
content = content.replace(block3_old, block3_new)

# 4. text contents
content = content.replace("document.getElementById('monitor-source-url').textContent = \\URL: \\\\;", "document.getElementById('monitor-source-url').textContent = `URL: ${url}`;")
content = content.replace("recentCount.textContent = \\\\ encontrados\\;", "recentCount.textContent = `${monitorData.recentVideos.length} encontrados`;")
content = content.replace("showAllBtn.innerHTML = \\<i class=\"fas fa-expand-arrows-alt\"></i> Ver todos os \\ vdeos extrados\\;", "showAllBtn.innerHTML = `<i class=\"fas fa-expand-arrows-alt\"></i> Ver todos os ${monitorData.recentVideos.length} vídeos extraídos`;")
content = content.replace("subtitle.textContent = \\Mostrando \\ vdeos de \\\\;", "subtitle.textContent = `Mostrando ${monitorData.recentVideos.length} vídeos de ${monitorData.username}`;")
content = content.replace("const readingTime = \\\\ min de leitura\\;", "const readingTime = `${minutes} min de leitura`;")

# 5. card.innerHTML in renderMonitorResults
block5_old = """            card.innerHTML = \\
                <p style="font-weight: 500; color: #111827; margin: 0 0 12px 0; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden;" title="\\">\\</p>
                <div style="display: flex; flex-wrap: wrap; align-items: center; gap: 12px; font-size: 14px; color: #6b7280;">
                    <div style="display: flex; align-items: center; gap: 4px;"><i class="fas fa-eye" style="color: #9ca3af;"></i> \\</div>
                    <div style="display: flex; align-items: center; gap: 4px;"><i class="fas fa-heart" style="color: #9ca3af;"></i> \\</div>
                    <div style="display: flex; align-items: center; gap: 4px;"><i class="far fa-calendar" style="color: #9ca3af;"></i> \\</div>
                </div>
            \\;"""
block5_new = """            card.innerHTML = `
                <p style="font-weight: 500; color: #111827; margin: 0 0 12px 0; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden;" title="${video.title}">${video.title}</p>
                <div style="display: flex; flex-wrap: wrap; align-items: center; gap: 12px; font-size: 14px; color: #6b7280;">
                    <div style="display: flex; align-items: center; gap: 4px;"><i class="fas fa-eye" style="color: #9ca3af;"></i> ${video.views}</div>
                    <div style="display: flex; align-items: center; gap: 4px;"><i class="fas fa-heart" style="color: #9ca3af;"></i> ${video.likes}</div>
                    <div style="display: flex; align-items: center; gap: 4px;"><i class="far fa-calendar" style="color: #9ca3af;"></i> ${video.date}</div>
                </div>
            `;"""
content = content.replace(block5_old, block5_new)

# 6. card.innerHTML in openAllVideosModal
block6_old = """        card.innerHTML = \\
            <div style="width: 32px; height: 32px; border-radius: 50%; background: #f3f4f6; display: flex; align-items: center; justify-content: center; color: #6b7280; font-weight: 700; font-size: 14px; flex-shrink: 0;">
                \\
            </div>
            <div>
                <p style="font-weight: 500; color: #111827; margin: 0 0 12px 0;" title="\\">\\</p>
                <div style="display: flex; flex-wrap: wrap; align-items: center; gap: 16px; font-size: 14px; color: #6b7280;">
                    <div style="display: flex; align-items: center; gap: 4px; background: #f9fafb; padding: 4px 8px; border-radius: 4px;"><i class="fas fa-eye" style="color: #9ca3af;"></i> <span style="font-weight: 500;">\\</span></div>
                    <div style="display: flex; align-items: center; gap: 4px; background: #f9fafb; padding: 4px 8px; border-radius: 4px;"><i class="fas fa-heart" style="color: #9ca3af;"></i> <span style="font-weight: 500;">\\</span></div>
                    <div style="display: flex; align-items: center; gap: 4px; background: #f9fafb; padding: 4px 8px; border-radius: 4px;"><i class="far fa-calendar" style="color: #9ca3af;"></i> <span style="font-weight: 500;">\\</span></div>
                </div>
            </div>
        \\;"""
block6_new = """        card.innerHTML = `
            <div style="width: 32px; height: 32px; border-radius: 50%; background: #f3f4f6; display: flex; align-items: center; justify-content: center; color: #6b7280; font-weight: 700; font-size: 14px; flex-shrink: 0;">
                ${index + 1}
            </div>
            <div>
                <p style="font-weight: 500; color: #111827; margin: 0 0 12px 0;" title="${video.title}">${video.title}</p>
                <div style="display: flex; flex-wrap: wrap; align-items: center; gap: 16px; font-size: 14px; color: #6b7280;">
                    <div style="display: flex; align-items: center; gap: 4px; background: #f9fafb; padding: 4px 8px; border-radius: 4px;"><i class="fas fa-eye" style="color: #9ca3af;"></i> <span style="font-weight: 500;">${video.views}</span></div>
                    <div style="display: flex; align-items: center; gap: 4px; background: #f9fafb; padding: 4px 8px; border-radius: 4px;"><i class="fas fa-heart" style="color: #9ca3af;"></i> <span style="font-weight: 500;">${video.likes}</span></div>
                    <div style="display: flex; align-items: center; gap: 4px; background: #f9fafb; padding: 4px 8px; border-radius: 4px;"><i class="far fa-calendar" style="color: #9ca3af;"></i> <span style="font-weight: 500;">${video.date}</span></div>
                </div>
            </div>
        `;"""
content = content.replace(block6_old, block6_new)

# 7. header.innerHTML in renderScriptsHistory
block7_old = """        header.innerHTML = \\
            <div style="display: flex; align-items: center; gap: 16px;">
                <div style="background: \\; color: \\; padding: 12px; border-radius: 8px;">
                    <i class="fas fa-file-alt" style="font-size: 20px;"></i>
                </div>
                <div>
                    <h3 style="font-weight: 600; color: #111827; margin: 0 0 4px 0;">\\</h3>
                    <div style="display: flex; align-items: center; gap: 12px; font-size: 14px; color: #6b7280;">
                        <span>\\</span>
                        <span style="width: 4px; height: 4px; border-radius: 50%; background: #d1d5db;"></span>
                        <span style="text-transform: capitalize;">\\</span>
                        <span style="width: 4px; height: 4px; border-radius: 50%; background: #d1d5db;"></span>
                        <span style="display: flex; align-items: center; gap: 4px;"><i class="far fa-clock"></i> \\</span>
                    </div>
                </div>
            </div>
        \\;"""
block7_new = """        header.innerHTML = `
            <div style="display: flex; align-items: center; gap: 16px;">
                <div style="background: ${iconBg}; color: ${iconColor}; padding: 12px; border-radius: 8px;">
                    <i class="fas fa-file-alt" style="font-size: 20px;"></i>
                </div>
                <div>
                    <h3 style="font-weight: 600; color: #111827; margin: 0 0 4px 0;">${script.title || 'Sem Título'}</h3>
                    <div style="display: flex; align-items: center; gap: 12px; font-size: 14px; color: #6b7280;">
                        <span>${typeName}</span>
                        <span style="width: 4px; height: 4px; border-radius: 50%; background: #d1d5db;"></span>
                        <span style="text-transform: capitalize;">${script.status || 'Gerado'}</span>
                        <span style="width: 4px; height: 4px; border-radius: 50%; background: #d1d5db;"></span>
                        <span style="display: flex; align-items: center; gap: 4px;"><i class="far fa-clock"></i> ${dateStr} - ${readingTime}</span>
                    </div>
                </div>
            </div>
        `;"""
content = content.replace(block7_old, block7_new)

io.open(filepath, 'w', encoding='utf-8').write(content)
print("Fix applied.")
