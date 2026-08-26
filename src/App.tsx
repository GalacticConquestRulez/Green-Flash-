import { useEffect } from "react";
import { Navigate, Route, Routes, useLocation } from "react-router-dom";
import { MobileCta, SiteChrome } from "@/components/chrome";
import { Hero } from "@/components/hero";
import {
  Benefits,
  FinalCta,
  Offer,
  Problem,
  Process,
  Proof,
  Services,
} from "@/components/sections";
import { PrivacyPage } from "@/pages/privacy";
import { TermsPage } from "@/pages/terms";

function ScrollToHash() {
  const { pathname, hash } = useLocation();
  useEffect(() => {
    if (hash) {
      const el = document.getElementById(hash.slice(1));
      if (el) {
        el.scrollIntoView({ behavior: "smooth", block: "start" });
        return;
      }
    }
    window.scrollTo({ top: 0 });
  }, [pathname, hash]);
  return null;
}

function Home() {
  return (
    <SiteChrome>
      <main id="main" className="pb-20 md:pb-0">
        <Hero />
        <Problem />
        <Services />
        <Process />
        <Offer />
        <Benefits />
        <Proof />
        <FinalCta />
      </main>
      <MobileCta />
    </SiteChrome>
  );
}

export default function App() {
  return (
    <>
      <ScrollToHash />
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/privacy" element={<PrivacyPage />} />
        <Route path="/terms" element={<TermsPage />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </>
  );
}
