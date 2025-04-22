"""
Enhanced progress bar for the FramePack AI Video Generator
"""

progress_html = '''
<div class="enhanced-loader-container">
  <div class="enhanced-progress-container">
    <div class="enhanced-progress-bar" style="width: *percentage*%;"></div>
  </div>
  <div class="enhanced-progress-info">
    <span class="enhanced-progress-percentage">*percentage*%</span>
    <span class="enhanced-progress-text">*text*</span>
  </div>
</div>
'''

css = '''
.enhanced-loader-container {
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Oxygen, Ubuntu, Cantarell, "Fira Sans", "Droid Sans", "Helvetica Neue", sans-serif;
  padding: 15px;
  margin-bottom: 20px;
}

.enhanced-progress-container {
  width: 100%;
  height: 12px;
  background-color: #f3f3f3;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1) inset;
  margin-bottom: 10px;
}

.enhanced-progress-bar {
  height: 100%;
  background: linear-gradient(90deg, #4f46e5 0%, #8b5cf6 100%);
  border-radius: 8px;
  transition: width 0.3s ease;
}

.enhanced-progress-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.enhanced-progress-percentage {
  font-size: 16px;
  font-weight: 600;
  color: #1e293b;
}

.enhanced-progress-text {
  font-size: 14px;
  color: #64748b;
}

.no-generating-animation > .generating {
  display: none !important;
}
'''


def make_enhanced_progress_bar_html(percentage, text):
    """Generate HTML for the enhanced progress bar"""
    return progress_html.replace('*percentage*', str(percentage)).replace('*text*', text)


def get_enhanced_progress_bar_css():
    """Get the CSS for the enhanced progress bar"""
    return css
