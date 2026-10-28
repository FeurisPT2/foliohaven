# replica-brand

Nothing launches under the original's identity. This skill is the line
between "a clone" and "your app".

Tool in this folder:

```bash
python3 sweep.py . --avoid "Original Name,Its Company" --domains original.com --colors "#006bff"
python3 sweep.py . --config replica/brand.json        # same, from the brand file
```

Writes `replica/brand.md` and `replica/brand.json` (`avoid`, `domains`,
`colors`, used by `sweep.py`, `listing.py` and replica-deploy).

## Step 6: the sweep

Replace every placeholder name, colour and string. Then:

```bash
python3 sweep.py . --config replica/brand.json
```

It searches file contents and file names for the original's name (also inside
identifiers like `CalendlyEmbed`), domains and colours, skipping
`node_modules`, build output and the `replica/` planning folder. Exit 1 means
something is left. Fix until it says clean. Also check by eye: the favicon,
the page titles, the email templates, the OG image, the app icon.
