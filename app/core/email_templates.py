from __future__ import annotations

from typing import Iterable
import os


def _join_lines(lines: Iterable[str]) -> str:
    return "\n\n".join(line.strip() for line in lines if line is not None and str(line).strip())


def render_action_email_html(
    *,
    title: str,
    heading: str,
    body_lines: Iterable[str],
    action_text: str,
    action_url: str,
    footer_lines: Iterable[str] | None = None,
) -> str:
    """Render a simple, dark-themed HTML email with a prominent CTA button.

    Keeps inline styles for broad email client support and avoids external assets.
    """
    app_name = os.getenv("APP_NAME", "SPACEBATTLE").strip() or "SPACEBATTLE"

    body_html = "".join(
        f"<p style=\"margin:0 0 14px;line-height:1.6;color:#c7d2fe\">{line}</p>" for line in body_lines
    )

    notice_html = ""
    if footer_lines:
        notice_html = (
            "<div style=\"margin-top:14px;border-radius:12px;border:1px solid rgba(16,185,129,.28);"
            "background:rgba(16,185,129,.08);padding:10px 12px\">"
            + "".join(
                f"<p style=\"margin:0 0 6px;line-height:1.55;color:#bbf7d0;font-weight:600\">{line}</p>"
                for line in footer_lines
            )
            + "</div>"
        )

    return f"""
<!doctype html>
<html lang=\"de\">
  <head>
    <meta charset=\"utf-8\" />
    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
    <title>{title}</title>
  </head>
  <body style=\"margin:0;padding:0;background:#0a0f1d;-webkit-text-size-adjust:100%;\">
    <table role=\"presentation\" width=\"100%\" cellpadding=\"0\" cellspacing=\"0\" border=\"0\" style=\"background:#0a0f1d;padding:40px 0 48px\">
      <tr>
        <td align=\"center\">
          <div style=\"font-family:ui-sans-serif,system-ui,-apple-system,Segoe UI,Roboto;text-transform:uppercase;letter-spacing:.18em;font-weight:800;color:#60a5fa;margin:10px 0 8px\">{app_name}</div>
          <div style=\"font-family:ui-sans-serif,system-ui,-apple-system,Segoe UI,Roboto;font-weight:900;color:#e5e7eb;font-size:28px;line-height:1.2;margin:0 0 8px\">{heading}</div>
          <div style=\"font-family:ui-sans-serif,system-ui,-apple-system,Segoe UI,Roboto;color:#9fb6d0;margin:0 0 22px\">{_join_lines(body_lines)}</div>

          <table role=\"presentation\" width=\"100%\" cellpadding=\"0\" cellspacing=\"0\" border=\"0\" style=\"max-width:620px\">
            <tr>
              <td align=\"center\">
                <table role=\"presentation\" cellpadding=\"0\" cellspacing=\"0\" border=\"0\" width=\"100%\" style=\"background:#0f172a;border-radius:16px;border:1px solid rgba(100,116,139,.32);padding:22px\">
                  <tr>
                    <td align=\"left\" style=\"font-family:ui-sans-serif,system-ui,-apple-system,Segoe UI,Roboto\">
                      <a href=\"{action_url}\" style=\"display:block;text-align:center;background:#3b82f6;color:#ffffff;text-decoration:none;padding:12px 18px;border-radius:10px;font-weight:800;letter-spacing:.02em\">{action_text}</a>
                      {notice_html}
                    </td>
                  </tr>
                </table>
              </td>
            </tr>
          </table>

          <div style=\"color:#6b7280;font-size:12px;margin-top:14px;font-family:ui-sans-serif,system-ui,-apple-system,Segoe UI,Roboto\">Diese E‑Mail wurde automatisch versendet. Bitte nicht beantworten.</div>
        </td>
      </tr>
    </table>
  </body>
  </html>
    """.strip()


def render_action_email_text(
    *, heading: str, body_lines: Iterable[str], action_text: str, action_url: str, footer_lines: Iterable[str] | None = None
) -> str:
    parts: list[str] = [heading, "", _join_lines(body_lines), "", f"{action_text}: {action_url}"]
    if footer_lines:
        parts.extend(["", _join_lines(footer_lines)])
    return "\n".join([p for p in parts if p is not None])
