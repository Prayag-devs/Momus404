"use client";

import { useEffect, useRef, useCallback } from "react";
import { X } from "lucide-react";

interface MomusLoreModalProps {
  isOpen: boolean;
  onClose: () => void;
}

const ASCII_LOGO = `
███╗   ███╗ ██████╗ ███╗   ███╗██╗   ██╗███████╗
████╗ ████║██╔═══██╗████╗ ████║██║   ██║██╔════╝
██╔████╔██║██║   ██║██╔████╔██║██║   ██║███████╗
██║╚██╔╝██║██║   ██║██║╚██╔╝██║██║   ██║╚════██║
██║ ╚═╝ ██║╚██████╔╝██║ ╚═╝ ██║╚██████╔╝███████║
╚═╝     ╚═╝ ╚═════╝ ╚═╝     ╚═╝ ╚═════╝ ╚══════╝
[ NOUS HERMES TERMINAL SKIN // PROTOCOL SPECIFICATION ]`.trim();

export default function MomusLoreModal({ isOpen, onClose }: MomusLoreModalProps) {
  const modalRef = useRef<HTMLDivElement>(null);
  const closeBtnRef = useRef<HTMLButtonElement>(null);

  // Focus trap
  useEffect(() => {
    if (!isOpen) return;
    const prev = document.activeElement as HTMLElement;
    closeBtnRef.current?.focus();

    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === "Escape") onClose();
      // Focus trap within modal
      if (e.key === "Tab" && modalRef.current) {
        const focusable = modalRef.current.querySelectorAll<HTMLElement>(
          'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
        );
        const first = focusable[0];
        const last = focusable[focusable.length - 1];
        if (e.shiftKey && document.activeElement === first) {
          e.preventDefault();
          last?.focus();
        } else if (!e.shiftKey && document.activeElement === last) {
          e.preventDefault();
          first?.focus();
        }
      }
    };

    window.addEventListener("keydown", handleKeyDown);
    return () => {
      window.removeEventListener("keydown", handleKeyDown);
      prev?.focus();
    };
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  return (
    <div
      role="dialog"
      aria-modal="true"
      aria-label="MOMUS Protocol Archives"
      className="hermes-modal"
      ref={modalRef}
    >
      <div className="hermes-modal__backdrop" onClick={onClose} aria-hidden="true" />

      <div className="hermes-modal__inner animate-slide-in-right relative z-10">
        {/* Close button — top right */}
        <button
          ref={closeBtnRef}
          onClick={onClose}
          aria-label="Close archive"
          className="absolute top-4 right-4 hermes-modal__close-btn flex items-center gap-1.5"
        >
          <X size={11} strokeWidth={2} />
          ESC / CLOSE ARCHIVE
        </button>

        {/* ASCII Logo */}
        <pre className="hermes-modal__ascii-logo" aria-hidden="true">
          {ASCII_LOGO}
        </pre>

        {/* Title */}
        <h2>
          ┌─[ ARCHIVES: THE MOMUS PROTOCOL ]─────────────────────────────────┐
        </h2>

        {/* Dossier content */}
        <section aria-label="Mythological background">
          <h2>§ I. ORIGIN // THE GREEK CONTEXT</h2>
          <p>
            <strong>Momus</strong> (Μῶμος) — Greek god of severe criticism, mockery, and fault-finding.
            Son of Night (<em>Nyx</em>). Dwelt among the Olympians as the sole voice willing
            to name imperfection in the works of gods. He found fault with Aphrodite for the
            creaking of her sandals. He mocked Hephaestus for placing the heart of a man on
            the outside of his clay figure where one could read it directly — a transparency
            he deemed a structural flaw. He was <strong>exiled from Olympus</strong> for these
            transgressions. The gods did not expel him because he was wrong. They expelled him
            because he was right.
          </p>
        </section>

        <hr className="hermes-modal__divider" />

        <section aria-label="Architecture rationale">
          <h2>§ II. WHY MOMUS RUNS AT THE EDGE</h2>
          <p>
            Modern QA systems fail for a predictable reason: they trust the cloud with the
            assertion boundary. Every <em>"did the button respond?"</em> question is routed to
            a probabilistic language model that has read Shakespeare and tax law but has never
            observed a DOM state in real time.
          </p>
          <p style={{ marginTop: "0.75rem" }}>
            <strong>MOMUS404</strong> inverts this. The assertion oracle — <strong>Laya 421M</strong>
            — lives on the operator's hardware, on a{" "}
            <span className="badge-green">NVIDIA Quadro P1000</span>, inside a 4 GB GDDR5 VRAM
            envelope, running FP16 inference in{" "}
            <span className="badge-amber">&lt;50 ms per step</span>. It does not phone home.
            It does not retry on quota limits. It does not hallucinate confidence.
          </p>
          <p style={{ marginTop: "0.75rem" }}>
            Cloud models — <strong>Nous Hermes</strong> for planning,{" "}
            <strong>OpenAI gpt-4o</strong> for healing — are invoked
            only when Laya renders a{" "}
            <span className="badge-amber">FAIL</span> verdict. This is the{" "}
            <em>hot-path rule</em>: <strong>edge judges first, cloud pays only on failure.</strong>
          </p>
        </section>

        <hr className="hermes-modal__divider" />

        <section aria-label="Zero leniency design philosophy">
          <h2>§ III. ZERO-LENIENCY DESIGN PHILOSOPHY</h2>
          <p>
            Fragile UI assumptions arise when test assertions are written against what the developer
            <em> intended</em> to ship rather than what the browser <em>actually rendered</em>.
            Momus, the unsparing critic, rejects this category error.
          </p>
          <ul style={{ marginTop: "0.75rem", paddingLeft: "1.5rem", listStyle: "none" }}>
            {[
              "Every step asserts the full accessibility tree, not a CSS selector that will change with the next refactor.",
              "Selector failures trigger self-healing (OpenAI) — not human escalation at 3 AM.",
              "Credentials never traverse the LLM context window. OpenDots Vault enforces this at the type level.",
              "RETRY verdicts re-snapshot the DOM and re-judge, tolerating transient spinner states without flapping.",
              "Audit trails are immutable: every MCP action, every Laya verdict, every heal attempt is logged and stored.",
            ].map((item, i) => (
              <li key={i} style={{ marginBottom: "0.5rem", color: "var(--herm-muted)", fontSize: "0.78rem" }}>
                <span style={{ color: "var(--herm-green)", marginRight: "0.5rem" }}>▶</span>
                {item}
              </li>
            ))}
          </ul>
        </section>

        <hr className="hermes-modal__divider" />

        <section aria-label="Component dossier">
          <h2>§ IV. COMPONENT DOSSIER</h2>
          <div style={{ display: "grid", gap: "0.6rem" }}>
            {[
              { badge: "LAYA 421M", color: "badge-green", desc: "Local edge judge. Pascal sm_61. FP16. &lt;50 ms. Zero token cost. Binary: PASS / FAIL / RETRY." },
              { badge: "NOUS HERMES", color: "badge-amber", desc: "Cloud planner. Converts Excel criteria into sequenced Gherkin-style action plans." },
              { badge: "OPENAI", color: "badge-amber", desc: "Fallback healer. Only invoked on FAIL. Self-heals selectors, escalates root causes, writes reports." },
              { badge: "OPENDOTS", color: "badge-green", desc: "Fernet vault. Credentials encrypted in memory. Injected into browser context out-of-band. Never logged." },
              { badge: "PLAYWRIGHT MCP", color: "badge-green", desc: "JSON-RPC 2.0 browser driver. Stable internal tool names survive server renames." },
            ].map((c) => (
              <div key={c.badge} style={{ display: "flex", alignItems: "flex-start", gap: "0.75rem" }}>
                <span className={c.color} style={{ whiteSpace: "nowrap", flexShrink: 0 }}>
                  [{c.badge}]
                </span>
                <span
                  style={{ color: "var(--herm-muted)", fontSize: "0.75rem" }}
                  dangerouslySetInnerHTML={{ __html: c.desc }}
                />
              </div>
            ))}
          </div>
        </section>

        <hr className="hermes-modal__divider" />

        {/* Footer */}
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: "1rem" }}>
          <p style={{ color: "var(--herm-muted)", fontSize: "0.7rem" }}>
            └─[ END OF ARCHIVE ]──────────────────────────────────────────────────┘
          </p>
          <button
            onClick={onClose}
            className="hermes-modal__close-btn"
            id="btn-lore-close"
          >
            [ ESC / CLOSE ARCHIVE ]
          </button>
        </div>
      </div>
    </div>
  );
}
