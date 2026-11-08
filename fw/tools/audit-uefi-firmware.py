#!/usr/bin/env python3
"""Fail-closed structural audit for candidate Peridot UEFI firmware inputs.

This tool does NOT convert ABL into a UEFI FD and does NOT produce a boot image.
It records bounded FV/PE candidates so a Peridot-specific FD can be assembled only
after the actual firmware layout has been identified.
"""
from __future__ import annotations
import argparse, hashlib, json, struct
from pathlib import Path

EFI_FV_GUID = bytes.fromhex("d9 54 93 7a 68 04 4a 44 81 ce 0b f6 17 d8 90 df")

def scan(path: Path):
    data = path.read_bytes()
    fvs, pes = [], []
    pos = 0
    while True:
        pos = data.find(b"_FVH", pos)
        if pos < 0: break
        # EFI_FIRMWARE_VOLUME_HEADER: _FVH is at offset 40; FvLength at 32.
        start = pos - 40
        if start >= 0 and start + 56 <= len(data):
            fv_len = struct.unpack_from("<Q", data, start + 32)[0]
            hdr_len = struct.unpack_from("<H", data, start + 48)[0]
            if 56 <= hdr_len <= fv_len and fv_len <= len(data) - start:
                fvs.append({"offset": start, "length": fv_len, "header_length": hdr_len,
                            "filesystem_guid": data[start+16:start+32].hex()})
        pos += 4
    for sig in (b"MZ",):
        pos = 0
        while True:
            pos = data.find(sig, pos)
            if pos < 0: break
            if pos + 0x40 <= len(data):
                peoff = struct.unpack_from("<I", data, pos + 0x3c)[0]
                pe = pos + peoff
                if peoff >= 0x40 and pe + 24 <= len(data) and data[pe:pe+4] == b"PE\0\0":
                    machine, sections, _, _, _, opt_size, _ = struct.unpack_from("<HHIIIHH", data, pe+4)
                    if 0 < sections <= 96 and opt_size <= 4096 and pe + 24 + opt_size <= len(data):
                        pes.append({"offset": pos, "pe_header_offset": pe, "machine": hex(machine),
                                    "sections": sections, "optional_header_size": opt_size})
            pos += 2
    return {"file": path.name, "size": len(data), "sha256": hashlib.sha256(data).hexdigest(),
            "firmware_volumes": fvs, "validated_pe_images": pes}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("images", nargs="+", type=Path)
    ap.add_argument("--json", type=Path)
    a = ap.parse_args()
    report = {"scope": "structural scan only; not a bootability verdict",
              "images": [scan(p) for p in a.images]}
    rendered = json.dumps(report, indent=2)
    print(rendered)
    if a.json: a.json.write_text(rendered + "\n")
if __name__ == "__main__": main()
