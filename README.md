# Midas Vergi - US Stock Tax Calculator

A comprehensive web application for calculating Turkish tax obligations on US stock transactions. This project demonstrates full-stack development skills with modern technologies and complex financial calculations.

## 🚀 Live Demo

[Add your deployed application URL here]

## ✨ Features

- **Automated Tax Calculations**: Upload transaction documents and get instant tax calculations
- **Multi-Broker Support**: Handles documents from various US brokerage firms
- **PDF Processing**: Advanced PDF parsing and data extraction
- **User Authentication**: Secure login system with NextAuth.js
- **Real-time Exchange Rates**: Integration with currency exchange APIs
- **Inflation Adjustments**: Automatic inflation calculations for tax compliance
- **Responsive Design**: Modern, mobile-friendly UI with Tailwind CSS

## 🛠️ Technology Stack

### Frontend
- **Next.js 15** - React framework with App Router
- **React 19** - Latest React with concurrent features
- **TypeScript** - Type-safe development
- **Tailwind CSS** - Utility-first CSS framework
- **Radix UI** - Accessible component primitives
- **Lucide React** - Beautiful icons
- **Framer Motion** - Smooth animations

### Backend
- **Next.js API Routes** - Server-side API endpoints
- **NextAuth.js** - Authentication and session management
- **Prisma ORM** - Type-safe database operations
- **PostgreSQL** - Relational database
- **Python** - Financial calculations and PDF processing

### Python Backend Services
- **PDF Processing**: `pdf-parse`, `pdf2json`, `pdfjs-dist`
- **Database Operations**: PostgreSQL with psycopg2
- **Financial Calculations**: Custom tax calculation algorithms
- **Data Extraction**: Automated table extraction from PDFs

### Development & Deployment
- **ESLint** - Code linting and formatting
- **PostCSS** - CSS processing
- **TypeScript** - Static type checking
- **Git** - Version control

## 📊 Database Schema

The application uses PostgreSQL with the following key models:
- **Users**: Authentication and usage tracking
- **Transactions**: Stock transaction records
- **Dividends**: Dividend payment records
- **Exchange Rates**: USD/TRY conversion data
- **Inflation Data**: YI-UFE inflation indices

## 🔧 Installation & Setup

### Prerequisites
- Node.js 18+ 
- Python 3.8+
- PostgreSQL 12+
- npm or yarn

### Environment Variables
Create a `.env` file in the root directory:

```env
# Database
DATABASE_URL="postgresql://username:password@localhost:5432/midas_tax"

# Authentication
NEXTAUTH_SECRET="your-secret-key"
NEXTAUTH_URL="http://localhost:3000"

# Python Database
PG_HOST="127.0.0.1"
PG_PORT="5432"
PG_USER="postgres"
PG_PASSWORD="your_password"
PG_DATABASE="midas_tax"
```

### Installation Steps

1. **Clone the repository**
   ```bash
   git clone https://github.com/BurakPozut/midas-vergi.git
   cd midas-vergi
   ```

2. **Install Node.js dependencies**
   ```bash
   npm install
   ```

3. **Install Python dependencies**
   ```bash
   cd python
   pip install -r requirements.txt
   cd ..
   ```

4. **Set up the database**
   ```bash
   npx prisma generate
   npx prisma db push
   ```

5. **Run the development server**
   ```bash
   npm run dev
   ```

6. **Open your browser**
   Navigate to [http://localhost:3000](http://localhost:3000)

## 🏗️ Project Structure

```
midas-vergi/
├── app/                    # Next.js App Router
│   ├── api/               # API endpoints
│   ├── auth/              # Authentication pages
│   └── tax/               # Tax calculation pages
├── components/             # React components
│   ├── ui/                # Reusable UI components
│   └── FileUploader.tsx   # File upload component
├── lib/                   # Utility functions
├── python/                # Python backend services
│   ├── extract_tables.py  # PDF processing
│   ├── tax_calculator_db.py # Tax calculations
│   └── requirements.txt   # Python dependencies
├── prisma/                # Database schema
└── schemas/               # TypeScript schemas
```

## 🔐 Authentication

The application uses NextAuth.js with:
- Email/password authentication
- Session management
- Protected routes
- User usage tracking

## 📈 Key Features Implementation

### PDF Processing Pipeline
- **File Upload**: Drag-and-drop interface with progress tracking
- **Data Extraction**: Python scripts parse transaction tables from PDFs
- **Data Validation**: Zod schemas ensure data integrity
- **Database Storage**: Structured storage in PostgreSQL

### Tax Calculation Engine
- **Transaction Analysis**: Processes buy/sell transactions
- **Capital Gains**: Calculates short-term and long-term gains
- **Dividend Processing**: Handles dividend income and withholding
- **Inflation Adjustments**: Applies Turkish inflation indices
- **Exchange Rate Integration**: Real-time USD/TRY conversions

### User Experience
- **Responsive Design**: Mobile-first approach with Tailwind CSS
- **Loading States**: Smooth loading animations
- **Error Handling**: Comprehensive error messages
- **Progress Tracking**: Real-time upload and processing status

## 🚀 Deployment

The application is designed for deployment on:
- **Vercel** (recommended for Next.js)
- **Railway** (for full-stack deployment)
- **AWS** (with proper configuration)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👨‍💻 Developer

**Burak Pozut**
- GitHub: [@BurakPozut](https://github.com/BurakPozut)
- LinkedIn: [Add your LinkedIn profile]

## 🔮 Future Enhancements

- [ ] Real-time notifications
- [ ] Advanced reporting features
- [ ] Mobile app development
- [ ] Integration with Turkish tax authority APIs
- [ ] Multi-language support
- [ ] Advanced analytics dashboard

---

⭐ **Star this repository if you find it helpful!**
