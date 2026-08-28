import { useEffect } from "react";
import { Route, Routes, useLocation } from "react-router-dom";
import { AdvertisingPage } from "@/pages/advertising";
import { HomePage } from "@/pages/home";
import { MerchPage } from "@/pages/merch";
import { NotFoundPage } from "@/pages/not-found";
import { PrivacyPage } from "@/pages/privacy";
import { TermsPage } from "@/pages/terms";
import { WebsitesPage } from "@/pages/websites";

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

export default function App() {
  return (
    <>
      <ScrollToHash />
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/advertising" element={<AdvertisingPage />} />
        <Route path="/merch" element={<MerchPage />} />
        <Route path="/websites" element={<WebsitesPage />} />
        <Route path="/privacy" element={<PrivacyPage />} />
        <Route path="/terms" element={<TermsPage />} />
        <Route path="*" element={<NotFoundPage />} />
      </Routes>
    </>
  );
}
