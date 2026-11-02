"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import {
  Heart,
  Menu,
  Search,
  ShoppingBag,
  UserRound,
  X,
} from "lucide-react";

import AnnouncementBar from "@/components/announcements/AnnouncementBar";
import BagDrawer from "@/components/BagDrawer";
import { useBag } from "@/components/BagProvider";
import SearchOverlay from "@/components/SearchOverlay";

export default function SiteHeader() {
  const [scrolled, setScrolled] = useState(false);
  const [search, setSearch] = useState(false);
  const [bag, setBag] = useState(false);
  const [mobile, setMobile] = useState(false);

  const { count } = useBag();

  // Handle scroll detection for sticky header state
  useEffect(() => {
    const handleScroll = () => setScrolled(window.scrollY > 24);
    handleScroll();

    window.addEventListener("scroll", handleScroll, { passive: true });
    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  // Keyboard shortcut (Cmd/Ctrl + K) for search overlay
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === "k") {
        e.preventDefault();
        setSearch(true);
      }
    };

    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, []);

  return (
    <>
      <AnnouncementBar />

      <header className={`site-header ${scrolled ? "is-scrolled" : ""}`}>
        <div className="header-inner">
          {/* Mobile menu trigger */}
          <button
            aria-label="Toggle menu"
            className="icon-btn mobile-toggle"
            onClick={() => setMobile(!mobile)}
          >
            {mobile ? <X /> : <Menu />}
          </button>

          {/* Brand logo */}
          <Link aria-label="EVU home" className="wordmark" href="/">
            EVU<span>•</span>
          </Link>

          {/* Navigation links */}
          <nav
            aria-label="Main navigation"
            className={mobile ? "nav-links mobile-open" : "nav-links"}
          >
            <Link href="/shop" onClick={() => setMobile(false)}>
              SHOP ALL
            </Link>
            <Link href="/shop?edit=new" onClick={() => setMobile(false)}>
              NEW ARRIVALS
            </Link>
            <Link href="/editorial" onClick={() => setMobile(false)}>
              THE JOURNAL
            </Link>
            <Link href="/about" onClick={() => setMobile(false)}>
              OUR HOUSE
            </Link>
          </nav>

          {/* Action buttons */}
          <div className="header-actions">
            <button
              aria-label="Search products"
              className="icon-btn search-action"
              onClick={() => setSearch(true)}
            >
              <Search size={19} />
            </button>

            <Link aria-label="Wishlist" className="icon-btn" href="/wishlist">
              <Heart size={19} />
            </Link>

            <Link aria-label="Account" className="icon-btn" href="/account">
              <UserRound size={19} />
            </Link>

            <button
              aria-label={`Shopping bag, ${count} items`}
              className="icon-btn bag-trigger"
              onClick={() => setBag(true)}
            >
              <ShoppingBag size={19} />
              <span className="bag-count">{count}</span>
            </button>
          </div>
        </div>
      </header>

      <SearchOverlay open={search} onClose={() => setSearch(false)} />
      <BagDrawer open={bag} onClose={() => setBag(false)} />
    </>
  );
}