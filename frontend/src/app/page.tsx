export default function Home() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center bg-gradient-to-br from-prism-50 via-white to-prism-100">
      <div className="text-center space-y-6 animate-fade-in">
        {/* Logo/Icon Placeholder */}
        <div className="w-20 h-20 mx-auto rounded-2xl bg-gradient-to-br from-prism-500 to-prism-700 flex items-center justify-center shadow-lg shadow-prism-500/25">
          <svg
            className="w-10 h-10 text-white"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
            xmlns="http://www.w3.org/2000/svg"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M13 10V3L4 14h7v7l9-11h-7z"
            />
          </svg>
        </div>

        {/* Title */}
        <h1 className="text-5xl font-bold tracking-tight text-gray-900">
          Prism<span className="text-prism-600">IQ</span>
        </h1>

        {/* Subtitle */}
        <p className="text-xl text-gray-600 max-w-md">
          Dynamic Pricing Copilot
        </p>

        {/* Description */}
        <p className="text-gray-500 max-w-lg mx-auto">
          AI-powered pricing recommendations with explainable insights, 
          backed by market data and machine learning.
        </p>

        {/* Status Badge */}
        <div className="flex items-center justify-center gap-2 pt-4">
          <span className="relative flex h-3 w-3">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75"></span>
            <span className="relative inline-flex rounded-full h-3 w-3 bg-green-500"></span>
          </span>
          <span className="text-sm text-gray-500">
            API Connected • v1.0.0
          </span>
        </div>
      </div>
    </main>
  );
}

