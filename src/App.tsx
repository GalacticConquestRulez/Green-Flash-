import { useEffect } from "react";
import { Route, Routes, useLocation } from "react-router-dom";
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
import { usePageMeta } from "@/lib/use-page-meta";
import { NotFoundPage } from "@/pages/not-found";
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
  usePageMeta({
    title: "Green Flash Advertising | Affordable Google & Meta Ads for Local Businesses",
    description:
      "Affordable AI-powered Google and Meta ads for small businesses. Business Growth Package $375/month, no long-term contract. You provide the content — we run the ads.",
    path: "/",
  });
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
        <Route path="*" element={<NotFoundPage />} />
      </Routes>
    </>
  );
}
