import React from 'react';
import db from '@/lib/db';
import CategoriesClient from './CategoriesClient';

export const dynamic = 'force-dynamic';

export default async function CategoriesPage() {
  const categories = db
    .prepare(`
    SELECT Category.*, Blog.name as blogName, Blog.domain as blogDomain,
           (SELECT COUNT(*) FROM Post WHERE Post.categoryId = Category.id) as postCount
    FROM Category
    LEFT JOIN Blog ON Category.blogId = Blog.id
    ORDER BY Category.name ASC
  `)
    .all() as any[];

  const blogs = db.prepare('SELECT id, name, domain FROM Blog ORDER BY name ASC').all() as any[];

  return (
    <div className="max-w-[1440px] mx-auto space-y-8 pb-16 animate-in fade-in duration-500">
      <CategoriesClient initialCategories={categories} blogs={blogs} />
    </div>
  );
}
