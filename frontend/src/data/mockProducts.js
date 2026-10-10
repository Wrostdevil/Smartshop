export const MOCK_PRODUCTS = [
  {
    id: "LAP101",
    name: "Dell Inspiron 15 AI Edition",
    brand: "Dell",
    category: "Laptops",
    price: 949,
    originalPrice: 1099,
    rating: 4.7,
    reviewCount: 128,
    availability: "IN_STOCK",
    stockCount: 14,
    image: "https://images.unsplash.com/photo-1588872657578-7efd1f1555ed?w=600&auto=format&fit=crop&q=80",
    description: "High-performance laptop engineered for developers, AI workloads, and multi-threaded Java applications.",
    specs: {
      processor: "Intel Core i7 13th Gen",
      ram: "16GB DDR5",
      storage: "512GB NVMe SSD",
      display: '15.6" FHD IPS (1920x1080)',
      graphics: "Intel Iris Xe",
      batteryLife: "9 Hours",
      os: "Windows 11 Pro"
    },
    aiSummary: {
      pros: ["16GB RAM is ideal for running Docker containers and JVM apps", "Solid build quality with thermal management", "Under $1000 budget"],
      cons: ["Integrated graphics (not for heavy 3D rendering)", "Average webcam quality"]
    },
    tags: ["Java", "AI Learning", "Development", "Under $1000"]
  },
  {
    id: "LAP102",
    name: "MacBook Air M3",
    brand: "Apple",
    category: "Laptops",
    price: 1099,
    originalPrice: 1199,
    rating: 4.9,
    reviewCount: 312,
    availability: "IN_STOCK",
    stockCount: 8,
    image: "https://images.unsplash.com/photo-1517336714731-489689fd1ca8?w=600&auto=format&fit=crop&q=80",
    description: "Ultra-thin, lightweight power station driven by the Apple M3 chip with unified memory for seamless AI prompt engineering.",
    specs: {
      processor: "Apple M3 (8-core CPU, 10-core GPU)",
      ram: "16GB Unified Memory",
      storage: "512GB SSD",
      display: '13.6" Liquid Retina',
      graphics: "10-core GPU",
      batteryLife: "18 Hours",
      os: "macOS Sonoma"
    },
    aiSummary: {
      pros: ["Incredible battery life & fanless silent operation", "M3 Neural Engine accelerates local LLM quantization", "Premium aluminum unibody"],
      cons: ["Slightly above $1000 tier", "Non-upgradeable memory"]
    },
    tags: ["Apple", "M3", "AI Learning", "Ultraportable"]
  },
  {
    id: "LAP103",
    name: "Lenovo Legion Slim 5 AI",
    brand: "Lenovo",
    category: "Laptops",
    price: 999,
    originalPrice: 1249,
    rating: 4.6,
    reviewCount: 89,
    availability: "LOW_STOCK",
    stockCount: 3,
    image: "https://images.unsplash.com/photo-1603302576837-37561b2e2302?w=600&auto=format&fit=crop&q=80",
    description: "Dedicated GPU laptop packed with NVIDIA RTX 4060 for hardware-accelerated machine learning model training.",
    specs: {
      processor: "AMD Ryzen 7 7840HS",
      ram: "16GB DDR5 (Expandable to 64GB)",
      storage: "1TB Gen4 SSD",
      display: '16" WQXGA 165Hz',
      graphics: "NVIDIA GeForce RTX 4060 (8GB VRAM)",
      batteryLife: "6 Hours",
      os: "Windows 11 Home"
    },
    aiSummary: {
      pros: ["NVIDIA RTX 4060 with CUDA cores for local PyTorch/TensorFlow", "Expandable RAM slots for future AI upgrades", "High refresh rate screen"],
      cons: ["Bulkier power brick", "Shorter battery life under full GPU load"]
    },
    tags: ["Machine Learning", "PyTorch", "RTX GPU", "Gaming"]
  },
  {
    id: "PHN201",
    name: "Samsung Galaxy S24 Ultra",
    brand: "Samsung",
    category: "Smartphones",
    price: 1199,
    originalPrice: 1299,
    rating: 4.8,
    reviewCount: 450,
    availability: "IN_STOCK",
    stockCount: 20,
    image: "https://images.unsplash.com/photo-1610945265064-0e34e5519bbf?w=600&auto=format&fit=crop&q=80",
    description: "Flagship mobile with Galaxy AI live translation, circle to search, and 200MP camera system.",
    specs: {
      processor: "Snapdragon 8 Gen 3 for Galaxy",
      ram: "12GB",
      storage: "256GB",
      display: '6.8" Dynamic AMOLED 2X 120Hz',
      camera: "200MP + 50MP + 12MP + 10MP",
      battery: "5000 mAh",
      os: "Android 14 with One UI 6.1"
    },
    aiSummary: {
      pros: ["Built-in Galaxy AI real-time translation & summarization", "Stunning 2600 nits outdoor display", "Integrated S-Pen stylus"],
      cons: ["High price point", "Large footprint"]
    },
    tags: ["Flagship", "AI Phone", "Camera King"]
  },
  {
    id: "AUD301",
    name: "Sony WH-1000XM5 Noise-Canceling",
    brand: "Sony",
    category: "Audio",
    price: 349,
    originalPrice: 399,
    rating: 4.9,
    reviewCount: 890,
    availability: "IN_STOCK",
    stockCount: 25,
    image: "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=600&auto=format&fit=crop&q=80",
    description: "Industry-leading active noise canceling headphones with dual processors and 8 microphones for focus work.",
    specs: {
      driver: "30mm Precision Driver",
      anc: "Auto NC Optimizer with V1 & QN1 processors",
      batteryLife: "30 Hours ANC On",
      weight: "250g",
      connectivity: "Bluetooth 5.2 / Multipoint",
      codecs: "LDAC, AAC, SBC"
    },
    aiSummary: {
      pros: ["Top-tier noise isolation for deep work and coding focus", "Ultra-light ergonomic fit", "Fast charging (3 mins = 3 hours)"],
      cons: ["Ear cups do not fold inward", "Touch control learning curve"]
    },
    tags: ["Audio", "Noise Canceling", "Focus", "Under $500"]
  },
  {
    id: "HOM401",
    name: "Roborock Q Revo MaxV AI Robot Vacuum",
    brand: "Roborock",
    category: "Home Appliances",
    price: 799,
    originalPrice: 999,
    rating: 4.7,
    reviewCount: 64,
    availability: "IN_STOCK",
    stockCount: 9,
    image: "https://images.unsplash.com/photo-1558317374-067fb5f30001?w=600&auto=format&fit=crop&q=80",
    description: "AI obstacle recognition camera system with automatic hot water mop washing and self-emptying dock.",
    specs: {
      suction: "7000 Pa HyperForce",
      navigation: "PreciSense LiDAR + Reactive AI RGB Camera",
      docking: "Auto Washing, Drying, Dust Emptying, Refilling",
      batteryLife: "180 Minutes",
      voiceControl: "Built-in AI Assistant 'Hello Rocky'"
    },
    aiSummary: {
      pros: ["Identifies pet waste, cables, and shoes automatically", "Hands-free dock holds dust for 7 weeks", "FlexiArm mop reaches wall corners"],
      cons: ["Dock requires significant floor space", "Initial setup takes mapping time"]
    },
    tags: ["Smart Home", "AI Cleaning", "Robotics"]
  }
];

export const CATEGORIES = ["All", "Laptops", "Smartphones", "Audio", "Home Appliances"];

export const BRANDS = ["All", "Dell", "Apple", "Lenovo", "Samsung", "Sony", "Roborock"];

export const USER_PROFILE = {
  name: "Alex Johnson",
  tier: "Prime",
  avatar: "https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=150&auto=format&fit=crop&q=80",
  email: "alex.j@shopsmart.ai",
  loyaltyPoints: 1250
};
