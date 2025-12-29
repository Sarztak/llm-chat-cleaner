const fs = require('fs');
const TurndownService = require('turndown');

// Read the HTML content
const html = fs.readFileSync('conversation.html', 'utf8');

// Initialize Turndown
const turndownService = new TurndownService();

// Convert HTML to Markdown
const markdown = turndownService.turndown(html);

// Write to a Markdown file
fs.writeFileSync('chat_convert_by_turndown.md', markdown);