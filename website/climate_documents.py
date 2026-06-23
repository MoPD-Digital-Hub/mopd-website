"""Climate document categories — matches mopd.gov.et/en/MoPDcoreDivision/climate/."""

from .models import Document

CLIMATE_CATEGORY_ORDER = (
    Document.ClimateCategory.MULTILATERAL,
    Document.ClimateCategory.STRATEGIES,
    Document.ClimateCategory.PROJECTS,
    Document.ClimateCategory.REPORTS,
    Document.ClimateCategory.COP28,
)

CLIMATE_CATEGORY_I18N = {
    Document.ClimateCategory.MULTILATERAL: 'page.climate_docs.cat.multilateral',
    Document.ClimateCategory.STRATEGIES: 'page.climate_docs.cat.strategies',
    Document.ClimateCategory.PROJECTS: 'page.climate_docs.cat.projects',
    Document.ClimateCategory.REPORTS: 'page.climate_docs.cat.reports',
    Document.ClimateCategory.COP28: 'page.climate_docs.cat.cop28',
}


def climate_doc_sections(queryset):
    """Group published climate documents into official tab sections."""
    docs_by_category = {}
    for doc in queryset:
        category = doc.climate_category or Document.ClimateCategory.REPORTS
        docs_by_category.setdefault(category, []).append(doc)

    sections = []
    for category in CLIMATE_CATEGORY_ORDER:
        documents = docs_by_category.get(category)
        if not documents:
            continue
        sections.append({
            'code': category,
            'label': Document.ClimateCategory(category).label,
            'i18n_key': CLIMATE_CATEGORY_I18N[category],
            'documents': documents,
        })
    return sections
