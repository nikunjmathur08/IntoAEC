import Navbar from "@/components/Navbar";
import HeroSection from "@/components/HeroSection";
import FeaturesGrid from "@/components/FeaturesGrid";
import UploadSection from "@/components/UploadSection";

export default function Page() {
  return (
    <main className="bg-gradient-to-br from-white to-gray-50 text-slate-800 min-h-screen">
      <Navbar />
      <HeroSection />
      <FeaturesGrid />
      <UploadSection />
    </main>
  );
}
