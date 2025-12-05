export interface GeneratedListing {
  title: string;
  description: string;
  pricePrediction: string;
  tags: string[];
  features: string[];
  platformSpecific: string;
}

export enum Platform {
  AMAZON = 'Amazon',
  SHOPIFY = 'Shopify',
  EBAY = 'eBay',
  MERCADO_LIVRE = 'Mercado Livre',
  SHOPEE = 'Shopee',
  MAGALU = 'Magalu',
  OLX = 'OLX'
}

export interface NavItem {
  label: string;
  href: string;
}

export interface FeatureCardProps {
  title: string;
  description: string;
  logo: string;
  bgColor: string;
  onClick?: () => void;
}