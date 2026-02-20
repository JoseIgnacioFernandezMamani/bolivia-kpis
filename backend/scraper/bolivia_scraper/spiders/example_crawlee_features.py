"""
Ejemplo de características avanzadas de Crawlee.
Este archivo muestra cómo aprovechar al máximo Crawlee.
NO se ejecuta automáticamente - es solo referencia.
"""
import logging
from datetime import datetime, timezone
from dataclasses import asdict

from crawlee.playwright_crawler import PlaywrightCrawler, PlaywrightCrawlingContext
from crawlee.proxy_configuration import ProxyConfiguration
from crawlee import Request

from bolivia_scraper import settings
from bolivia_scraper.items import ElectionResultItem

logger = logging.getLogger(__name__)


class AdvancedCrawleeSpider:
    """
    Ejemplo de spider con características avanzadas de Crawlee:
    - Uso de Storage nativo (en lugar de pipelines custom)
    - Proxy rotation
    - Session management
    - Request prioritization
    - Error handling mejorado
    """

    name = "advanced_example"

    async def run(self) -> None:
        """Run the crawler with advanced features."""
        
        # 1. Configuración de proxies (opcional)
        # proxy_config = ProxyConfiguration(
        #     proxy_urls=[
        #         "http://proxy1.example.com:8000",
        #         "http://proxy2.example.com:8000",
        #     ]
        # )
        
        crawler = PlaywrightCrawler(
            max_requests_per_crawl=settings.MAX_REQUESTS_PER_CRAWL or None,
            max_request_retries=settings.MAX_REQUEST_RETRIES,
            max_concurrency=settings.MAX_CONCURRENCY,
            min_concurrency=settings.MIN_CONCURRENCY,
            request_handler_timeout_secs=settings.REQUEST_HANDLER_TIMEOUT_SECS,
            headless=settings.HEADLESS,
            browser_type=settings.BROWSER_TYPE,
            # proxy_configuration=proxy_config,  # Descomentar para usar proxies
        )

        @crawler.router.default_handler
        async def handle_default(context: PlaywrightCrawlingContext) -> None:
            """Handler por defecto con características avanzadas."""
            
            # Acceso a metadata del request
            logger.info(
                f"Processing: {context.request.url} "
                f"(retry: {context.request.retry_count}, "
                f"label: {context.request.label or 'default'})"
            )

            await context.page.wait_for_load_state("networkidle")
            
            # 1. GUARDAR EN DATASET (alternativa a pipelines)
            # Los datos se guardarán automáticamente en:
            # data/storage/datasets/default/*.json
            await context.push_data({
                "url": context.request.url,
                "title": await context.page.title(),
                "scraped_at": datetime.now(timezone.utc).isoformat(),
            })

            # 2. GUARDAR EN KEY-VALUE STORE (para datos únicos)
            # Útil para guardar configuraciones, metadatos, etc.
            await context.set_key_value_store_value(
                key="last_crawl_metadata",
                value={
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "url": context.request.url,
                    "status": "completed",
                }
            )

            # 3. LEER DEL KEY-VALUE STORE
            metadata = await context.get_key_value_store_value("last_crawl_metadata")
            if metadata:
                logger.info(f"Previous crawl: {metadata['timestamp']}")

            # 4. AGREGAR REQUESTS CON PRIORIDAD
            # Priority: números más bajos = mayor prioridad
            links = await context.page.query_selector_all("a[href]")
            for link in links[:10]:  # Solo primeros 10 para el ejemplo
                href = await link.get_attribute("href")
                if href:
                    await context.add_requests([
                        Request.from_url(
                            url=context.request.urljoin(href),
                            label="detail_page",
                            user_data={"referrer": context.request.url},
                            priority=1,  # Mayor prioridad
                        )
                    ])

        @crawler.router.handler("detail_page")
        async def handle_detail(context: PlaywrightCrawlingContext) -> None:
            """Handler para páginas de detalle."""
            
            # Acceso a user_data del request padre
            referrer = context.request.user_data.get("referrer")
            logger.info(f"Detail page {context.request.url} (from {referrer})")

            # Extraer datos y guardar
            title = await context.page.title()
            content = await context.page.inner_text("body")
            
            await context.push_data({
                "url": context.request.url,
                "title": title,
                "content_length": len(content),
                "referrer": referrer,
                "scraped_at": datetime.now(timezone.utc).isoformat(),
            })

        @crawler.failed_request_handler
        async def handle_failed(context: PlaywrightCrawlingContext, error: Exception) -> None:
            """Manejo personalizado de errores."""
            logger.error(
                f"Request failed: {context.request.url} "
                f"after {context.request.retry_count} retries. "
                f"Error: {error}"
            )
            
            # Guardar información de errores
            await context.push_data({
                "url": context.request.url,
                "error": str(error),
                "retry_count": context.request.retry_count,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }, dataset_name="failed_requests")

        # Ejecutar crawler
        start_urls = [
            "https://www.oep.org.bo/proceso-electoral/elecciones-generales/",
        ]
        
        await crawler.run(start_urls)
        
        # 5. EXPORTAR DATASETS
        # Los datasets se pueden exportar en múltiples formatos
        # Crawlee soporta: JSON, CSV, XML, RSS, Excel
        # Los archivos se crean automáticamente en:
        # data/storage/datasets/default/
        
        logger.info("Crawl completed. Check data/storage/datasets/ for results")


# ════════════════════════════════════════════════════════════════════════════
# CARACTERÍSTICAS ADICIONALES DE CRAWLEE
# ════════════════════════════════════════════════════════════════════════════

"""
1. AUTOSCALED POOL
   - Ajusta automáticamente la concurrencia según el rendimiento
   - Se activa automáticamente, sin configuración adicional

2. SESSION POOL
   - Mantiene sesiones de navegador para simular usuarios reales
   - Útil para sitios que bloquean scrapers
   
   session_pool_options = {
       "max_pool_size": 10,
       "session_options": {
           "max_age_secs": 600,
           "max_usage_count": 50,
       }
   }

3. REQUEST QUEUE PERSISTENCE
   - La cola de requests se guarda en disco
   - Si el crawler falla, puede continuar desde donde se quedó
   - Archivos en: data/storage/request_queues/

4. ESTADÍSTICAS
   - Crawlee registra automáticamente estadísticas:
     * Requests totales
     * Requests exitosos/fallidos
     * Velocidad de crawling
     * Uso de memoria
   - Accesibles en crawler.statistics

5. LIMPIEZA DE HTML
   - Crawlee puede limpiar HTML automáticamente
   - Útil para extraer texto limpio

6. SCREENSHOTS Y PDFs
   - Fácil captura de pantallas:
     await context.page.screenshot(path="screenshot.png")
   - Generación de PDFs:
     await context.page.pdf(path="page.pdf")

7. INTERCEPCIÓN DE REQUESTS
   - Bloquear recursos innecesarios (imágenes, CSS, fonts)
   - Mejora significativa de rendimiento
   
   async def block_resources(route, request):
       if request.resource_type in ["image", "stylesheet", "font"]:
           await route.abort()
       else:
           await route.continue_()
   
   # En el handler:
   await context.page.route("**/*", block_resources)
"""
