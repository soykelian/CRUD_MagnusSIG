# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Users

Administrators and sellers who manage or consult the inventory of a workplace safety company. The project is built by a university team; that context does not change the intended day-to-day users.

## Product Purpose

Magnus SIG supports the inventory operation of a workplace safety company. It organizes equipment, personal protective equipment (PPE/EPP), workwear, and other safety supplies, and helps staff review stock and trace recorded changes.

## Operating Context

The project is developed in phases by a university class team. The current application is a Django web app used locally during development. Its Spanish language and currency use the Colombian operating context.

## Capabilities and Constraints

The current web interface supports sign-in and role-based access; a dashboard; product and category management; stock status; inventory movements; purchase entries and sales/delivery exits; supplier and client records; inventory reports and CSV exports; inventory settings; and administrator access to Django administration. These screens use the application's saved database records. Do not invent safety certifications, compliance status, PPE inspections, or safety incidents: those workflows are not part of the implemented system.

## Brand Commitments

The product name is Magnus SIG. Preserve the supplied Magnus logo and its indigo, cyan, and orange identity. The management interface uses the requested clean operational layout and brand colors, suited to scanning stock and safety supplies.

## Evidence on Hand

The repository contains the Django application under `magnus_sig/`, operational templates under `magnus_sig/productos/templates/productos/`, and the original Magnus logo in the static branding assets. The user supplied Nexo inventory dashboard and management screen references, including its navigation icon set, as the target for this redesign. Data displayed in the app comes from saved records; do not add mock records.

## Product Principles

- Keep stock, catalog, and movement information traceable to saved records.
- Make equipment and personal protective supplies easy to classify and find.
- Make common inventory tasks easy to scan and perform.
- Respect administrator and seller permissions.
- Do not present unimplemented workflows or illustrative figures as live data.
