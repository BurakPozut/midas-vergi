import FileUploader from '../components/FileUploader';

export default function Home() {
  return (
    <div className="min-h-screen bg-gradient-to-b from-gray-900 to-navy-900">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-28">
        {/* Hero Section */}
        <div className="text-center space-y-8 mb-16">
          <h1 className="animate-fade-in text-5xl md:text-6xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-blue-400 to-emerald-400">
            ABD Hisse Senedi Vergi Hesaplayıcı
          </h1>
          <p className="animate-fade-in animation-delay-200 text-gray-400 text-lg md:text-xl max-w-2xl mx-auto">
            Otomatik aracımızla ABD hisse senedi vergi hesaplamalarınızı kolaylaştırın. Sadece işlem dökümünüzü yükleyin ve gerisini bize bırakın.
          </p>
        </div>

        {/* Features Grid */}
        <div className="grid md:grid-cols-3 gap-8 mb-16">
          {[
            {
              title: "Otomatik Hesaplama",
              description: "Dökümünüzü yükleyin ve anında vergi hesaplamalarını alın",
              icon: (
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 7h6m0 10v-3m-3 3h.01M9 17h.01M9 14h.01M12 14h.01M15 11h.01M12 11h.01M9 11h.01M7 21h10a2 2 0 002-2V5a2 2 0 00-2-2H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
                </svg>
              ),
            },
            {
              title: "Çoklu Aracı Kurumlar",
              description: "Çeşitli ABD aracı kurumlarından gelen dökümleri destekler",
              icon: (
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M21 13.255A23.931 23.931 0 0112 15c-3.183 0-6.22-.62-9-1.745M16 6V4a2 2 0 00-2-2h-4a2 2 0 00-2 2v2m4 6h.01M5 20h14a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                </svg>
              ),
            },
            {
              title: "Vergi Mevzuatı",
              description: "En güncel vergi düzenlemeleriyle uyumlu",
              icon: (
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
                </svg>
              ),
            },
          ].map((feature) => (
            <div
              key={feature.title}
              className="animate-fade-in animation-delay-200 bg-navy-800 p-6 rounded-xl hover:scale-105 transition-transform duration-300"
            >
              <div className="text-blue-400 mb-4">{feature.icon}</div>
              <h3 className="text-xl font-semibold text-white mb-2">{feature.title}</h3>
              <p className="text-gray-400">{feature.description}</p>
            </div>
          ))}
        </div>

        {/* Upload Section */}
        <div className="animate-fade-in animation-delay-400 bg-gray-800 rounded-lg p-8 shadow-xl">
          <h2 className="text-2xl font-bold text-white mb-4">
            Dökümünüzü Yükleyin
          </h2>
          <FileUploader />
        </div>
      </div>
    </div>
  );
}
