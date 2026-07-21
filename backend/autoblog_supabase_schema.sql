-- Schema para o Auto Blog CMS (Supabase / PostgreSQL)

-- 1. Blog
CREATE TABLE IF NOT EXISTS "Blog" (
    "id" TEXT NOT NULL PRIMARY KEY,
    "domain" TEXT NOT NULL,
    "name" TEXT NOT NULL,
    "niche" TEXT NOT NULL,
    "description" TEXT,
    "theme" TEXT NOT NULL DEFAULT 'dark',
    "primaryColor" TEXT DEFAULT '#3b82f6',
    "secondaryColor" TEXT DEFAULT '#1e40af',
    "layoutStyle" TEXT DEFAULT 'magazine',
    "createdAt" TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    "updatedAt" TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- 2. Category
CREATE TABLE IF NOT EXISTS "Category" (
    "id" TEXT NOT NULL PRIMARY KEY,
    "name" TEXT NOT NULL,
    "slug" TEXT NOT NULL,
    "blogId" TEXT NOT NULL,
    CONSTRAINT "Category_blogId_fkey" FOREIGN KEY ("blogId") REFERENCES "Blog" ("id") ON DELETE CASCADE ON UPDATE CASCADE
);

-- 3. Post
CREATE TABLE IF NOT EXISTS "Post" (
    "id" TEXT NOT NULL PRIMARY KEY,
    "title" TEXT NOT NULL,
    "slug" TEXT NOT NULL,
    "contentMd" TEXT NOT NULL,
    "contentHtml" TEXT NOT NULL,
    "coverImage" TEXT,
    "author" TEXT NOT NULL DEFAULT 'Redação IA',
    "isPublished" BOOLEAN NOT NULL DEFAULT false,
    "publishedAt" TIMESTAMP WITH TIME ZONE,
    "createdAt" TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    "updatedAt" TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    "metaTitle" TEXT,
    "metaDesc" TEXT,
    "blogId" TEXT NOT NULL,
    "categoryId" TEXT,
    "views" INTEGER DEFAULT 0,
    "language" TEXT DEFAULT 'pt',
    "translationGroupId" TEXT,
    CONSTRAINT "Post_blogId_fkey" FOREIGN KEY ("blogId") REFERENCES "Blog" ("id") ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT "Post_categoryId_fkey" FOREIGN KEY ("categoryId") REFERENCES "Category" ("id") ON DELETE SET NULL ON UPDATE CASCADE
);

-- 4. AdPlacement
CREATE TABLE IF NOT EXISTS "AdPlacement" (
    "id" TEXT NOT NULL PRIMARY KEY,
    "type" TEXT NOT NULL,
    "htmlCode" TEXT NOT NULL,
    "blogId" TEXT NOT NULL,
    CONSTRAINT "AdPlacement_blogId_fkey" FOREIGN KEY ("blogId") REFERENCES "Blog" ("id") ON DELETE CASCADE ON UPDATE CASCADE
);

-- 5. AgentConfig
CREATE TABLE IF NOT EXISTS "AgentConfig" (
    "id" TEXT NOT NULL PRIMARY KEY,
    "personaPrompt" TEXT NOT NULL,
    "imageStylePrompt" TEXT NOT NULL,
    "postFrequency" INTEGER NOT NULL DEFAULT 1,
    "isActive" BOOLEAN NOT NULL DEFAULT true,
    "blogId" TEXT NOT NULL,
    "youtubeChannelId" TEXT,
    "youtubeLastVideoId" TEXT,
    "localMemory" TEXT DEFAULT '',
    "instagramHandle" TEXT DEFAULT '',
    "instagramLastPost" TEXT DEFAULT '',
    "twitterHandle" TEXT DEFAULT '',
    "twitterLastTweet" TEXT DEFAULT '',
    "newsletterLastSent" TIMESTAMP WITH TIME ZONE,
    "rssSniperUrl" TEXT,
    "rssLastGuid" TEXT,
    "telegramBotToken" TEXT,
    "telegramChatId" TEXT,
    "postIntervalHours" INTEGER DEFAULT 4,
    "discordWebhookUrl" TEXT,
    "whatsappApiUrl" TEXT,
    "whatsappGroupId" TEXT,
    CONSTRAINT "AgentConfig_blogId_fkey" FOREIGN KEY ("blogId") REFERENCES "Blog" ("id") ON DELETE CASCADE ON UPDATE CASCADE
);

-- 6. Subscriber
CREATE TABLE IF NOT EXISTS "Subscriber" (
    "id" TEXT PRIMARY KEY,
    "email" TEXT,
    "blogId" TEXT,
    "createdAt" TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE("email", "blogId")
);

-- 7. Ads
CREATE TABLE IF NOT EXISTS "Ads" (
    "id" TEXT PRIMARY KEY,
    "blogId" TEXT NOT NULL,
    "type" TEXT NOT NULL,
    "code" TEXT NOT NULL,
    "isActive" INTEGER DEFAULT 1,
    UNIQUE("blogId", "type")
);

-- 8. PostCategory
CREATE TABLE IF NOT EXISTS "PostCategory" (
    "postId" TEXT NOT NULL,
    "categoryId" TEXT NOT NULL,
    PRIMARY KEY("postId", "categoryId")
);

-- 9. SocialSnippet
CREATE TABLE IF NOT EXISTS "SocialSnippet" (
    "id" TEXT PRIMARY KEY,
    "postId" TEXT NOT NULL,
    "platform" TEXT NOT NULL,
    "content" TEXT NOT NULL,
    UNIQUE("postId", "platform")
);

-- 10. Comment
CREATE TABLE IF NOT EXISTS "Comment" (
    "id" TEXT PRIMARY KEY,
    "postId" TEXT NOT NULL,
    "authorName" TEXT NOT NULL,
    "authorAvatar" TEXT NOT NULL,
    "content" TEXT NOT NULL,
    "createdAt" TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 11. AffiliateLink
CREATE TABLE IF NOT EXISTS "AffiliateLink" (
    "id" TEXT PRIMARY KEY,
    "blogId" TEXT NOT NULL,
    "keyword" TEXT NOT NULL,
    "url" TEXT NOT NULL,
    "createdAt" TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    "trackingCode" TEXT,
    "estimatedCpc" REAL DEFAULT 0.50,
    "totalClicks" INTEGER DEFAULT 0
);

-- 12. ContentQueue
CREATE TABLE IF NOT EXISTS "ContentQueue" (
    "id" TEXT PRIMARY KEY,
    "blogId" TEXT NOT NULL,
    "topic" TEXT NOT NULL,
    "status" TEXT DEFAULT 'pending',
    "createdAt" TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 13. NewsletterCampaign
CREATE TABLE IF NOT EXISTS "NewsletterCampaign" (
    "id" TEXT PRIMARY KEY,
    "blogId" TEXT,
    "subject" TEXT,
    "contentHtml" TEXT,
    "sentCount" INTEGER,
    "createdAt" TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 14. DailyViewLog
CREATE TABLE IF NOT EXISTS "DailyViewLog" (
    "id" TEXT PRIMARY KEY,
    "blogId" TEXT,
    "postId" TEXT,
    "date" TEXT,
    "views" INTEGER DEFAULT 0
);

-- 15. AffiliateClick
CREATE TABLE IF NOT EXISTS "AffiliateClick" (
    "id" TEXT PRIMARY KEY,
    "blogId" TEXT NOT NULL,
    "postId" TEXT,
    "affiliateLinkId" TEXT,
    "linkUrl" TEXT NOT NULL,
    "linkLabel" TEXT,
    "clickedAt" TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    "ipHash" TEXT,
    "country" TEXT DEFAULT 'BR',
    "revenue" REAL DEFAULT 0
);
