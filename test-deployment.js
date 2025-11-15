const { chromium } = require('playwright');

async function testDeployment() {
  console.log('🚀 Starting Playwright deployment test...\n');

  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext();
  const page = await context.newPage();

  try {
    // Test 1: Homepage loads
    console.log('Test 1: Loading homepage...');
    const response = await page.goto('https://aivesto.vercel.app', {
      waitUntil: 'networkidle',
      timeout: 30000
    });

    const statusCode = response.status();
    console.log(`✅ Homepage status: ${statusCode}`);

    if (statusCode !== 200) {
      console.log(`❌ Homepage failed with status ${statusCode}`);
      await browser.close();
      return;
    }

    // Test 2: Check article cards are present
    console.log('\nTest 2: Checking article cards...');
    const articleCards = await page.$$('.article-card');
    console.log(`✅ Found ${articleCards.length} article cards`);

    if (articleCards.length === 0) {
      console.log('❌ No article cards found');
      await browser.close();
      return;
    }

    // Test 3: Click first article and check for 404
    console.log('\nTest 3: Testing article link...');
    const firstCard = articleCards[0];

    // Get article URL before clicking
    const articleUrl = await firstCard.evaluate(el => {
      const titleEl = el.querySelector('.article-title');
      return titleEl ? titleEl.textContent : 'Unknown';
    });
    console.log(`📄 Testing article: ${articleUrl.substring(0, 50)}...`);

    // Click the article
    await firstCard.click();
    await page.waitForLoadState('networkidle', { timeout: 30000 });

    const currentUrl = page.url();
    const articleResponse = await page.goto(currentUrl, { waitUntil: 'networkidle' });
    const articleStatus = articleResponse.status();

    console.log(`📍 Article URL: ${currentUrl}`);
    console.log(`📊 Article status: ${articleStatus}`);

    if (articleStatus === 404) {
      console.log('❌ 404 ERROR DETECTED!');

      // Take screenshot
      await page.screenshot({ path: 'error-404.png', fullPage: true });
      console.log('📸 Screenshot saved: error-404.png');

      // Get page content
      const bodyText = await page.textContent('body');
      console.log('\n📄 Page content preview:');
      console.log(bodyText.substring(0, 500));

    } else if (articleStatus === 200) {
      console.log('✅ Article loaded successfully!');

      // Check for article content
      const hasContent = await page.$('.content');
      if (hasContent) {
        console.log('✅ Article content found');
      } else {
        console.log('⚠️  Article content not found');
      }

    } else {
      console.log(`⚠️  Unexpected status code: ${articleStatus}`);
    }

    // Test 4: Test multiple articles
    console.log('\nTest 4: Testing all article links...');
    await page.goto('https://aivesto.vercel.app');
    await page.waitForLoadState('networkidle');

    const allCards = await page.$$('.article-card');
    let successCount = 0;
    let failCount = 0;

    for (let i = 0; i < Math.min(allCards.length, 3); i++) {
      const card = allCards[i];
      const title = await card.evaluate(el =>
        el.querySelector('.article-title')?.textContent || 'Unknown'
      );

      await card.click();
      await page.waitForLoadState('networkidle');

      const url = page.url();
      const resp = await page.goto(url, { waitUntil: 'networkidle' });
      const status = resp.status();

      if (status === 200) {
        successCount++;
        console.log(`  ✅ [${i+1}/${Math.min(allCards.length, 3)}] ${title.substring(0, 40)}... → ${status}`);
      } else {
        failCount++;
        console.log(`  ❌ [${i+1}/${Math.min(allCards.length, 3)}] ${title.substring(0, 40)}... → ${status}`);
      }

      await page.goBack();
      await page.waitForLoadState('networkidle');
    }

    console.log(`\n📊 Summary: ${successCount} succeeded, ${failCount} failed`);

  } catch (error) {
    console.error('❌ Test error:', error.message);
  } finally {
    await browser.close();
    console.log('\n✅ Test completed');
  }
}

testDeployment();
