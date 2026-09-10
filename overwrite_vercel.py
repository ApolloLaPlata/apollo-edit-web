import json
with open('E:/MEUS PROGRAMAS/APOLLO_EDIT_WEB/vercel.json', 'w', encoding='utf-8') as f:
    f.write('''{
    "framework": null,
    "buildCommand": null,
    "outputDirectory": "public",
    "redirects": [
        {
            "source": "/web_ui/(.*)",
            "destination": "/$1",
            "permanent": false
        }
    ],
    "rewrites": [
        {
            "source": "/media/(.*)",
            "destination": "http://163.176.135.59/media/$1"
        },
        {
            "source": "/api/(.*)",
            "destination": "http://163.176.135.59/api/$1"
        },
        {
            "destination": "/pocket_director.html",
            "source": "/chat"
        }
    ]
}''')
