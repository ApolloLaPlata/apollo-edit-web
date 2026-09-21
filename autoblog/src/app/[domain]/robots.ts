import { MetadataRoute } from 'next';

export default async function robots(props: { params: Promise<{ domain: string }> }): Promise<MetadataRoute.Robots> {
  const params = await props.params;
  const decodedDomain = decodeURIComponent(params.domain);
  const baseUrl = `https://${decodedDomain}`;

  return {
    rules: {
      userAgent: '*',
      allow: '/',
      disallow: ['/api/', '/admin/'],
    },
    sitemap: `${baseUrl}/sitemap.xml`,
  };
}
