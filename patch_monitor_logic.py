import os

filepath = r'E:\MEUS PROGRAMAS\APOLLO_STUDIO\web_ui\monitor_logic.js'
with open(filepath, 'r', encoding='latin-1') as f:
    content = f.read()

target = """function openAllVideosModal() {
    if (!currentMonitorData || !currentMonitorData.recentVideos) return;
    // Simple alert for now showing all titles
    const titles = currentMonitorData.recentVideos.map((v, i) => `${i+1}. ${v.title}`).join('\\n');
    alert('Todos os vídeos extraídos:\\n\\n' + titles);
}"""

# Using robust parsing just in case encoding issues alter characters
replacement = """function openAllVideosModal() {
    if (!currentMonitorData || !currentMonitorData.recentVideos) return;
    
    const modal = document.getElementById('monitor-all-videos-modal');
    const grid = document.getElementById('monitor-all-videos-grid');
    const subtitle = document.getElementById('monitor-modal-subtitle');
    
    if (!modal || !grid) return;
    
    grid.innerHTML = '';
    subtitle.innerText = `${currentMonitorData.recentVideos.length} vídeos extraídos do perfil`;
    
    currentMonitorData.recentVideos.forEach(v => {
        const card = document.createElement('div');
        card.style.background = '#f9fafb';
        card.style.borderRadius = '12px';
        card.style.overflow = 'hidden';
        card.style.border = '1px solid #e5e7eb';
        card.style.display = 'flex';
        card.style.flexDirection = 'column';
        
        card.innerHTML = `
            <div style="aspect-ratio: 16/9; position: relative; background: #e5e7eb;">
                <img src="/api/proxy-image?url=${encodeURIComponent(v.thumbnail)}" style="width: 100%; height: 100%; object-fit: cover;" onerror="this.src='${v.thumbnail}'">
                <span style="position: absolute; bottom: 8px; right: 8px; background: rgba(0,0,0,0.8); color: white; font-size: 11px; padding: 2px 6px; border-radius: 4px;">
                    ${v.duration}
                </span>
            </div>
            <div style="padding: 12px; flex: 1; display: flex; flex-direction: column;">
                <h4 style="font-size: 13px; font-weight: 600; color: #111827; margin: 0 0 8px 0; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; text-overflow: ellipsis;">
                    ${v.title}
                </h4>
                <div style="margin-top: auto; display: flex; align-items: center; gap: 12px; font-size: 12px; color: #6b7280;">
                    <span title="Visualizações"><i class="fas fa-eye"></i> ${v.views}</span>
                    <span title="Publicado"><i class="far fa-clock"></i> ${v.published}</span>
                </div>
            </div>
        `;
        grid.appendChild(card);
    });
    
    modal.style.display = 'flex';
}

function closeAllVideosModal() {
    const modal = document.getElementById('monitor-all-videos-modal');
    if (modal) modal.style.display = 'none';
}"""

if "closeAllVideosModal" not in content:
    # We find the index of "function openAllVideosModal()" and replace from there
    idx = content.find("function openAllVideosModal()")
    if idx != -1:
        end_idx = content.find("}", idx) + 1
        content = content[:idx] + replacement + content[end_idx:]
        with open(filepath, 'w', encoding='latin-1') as f:
            f.write(content)
        print("monitor_logic.js patched!")
    else:
        print("openAllVideosModal not found.")
else:
    print("Already patched.")
