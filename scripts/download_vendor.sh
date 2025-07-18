# I'm not a frontend dev, so it works pretty stupid...
echo "- Creating vendor dirs"
mkdir -p ${VENDOR} \
    ${VENDOR}/ace \
    ${VENDOR}/bootstrap \
    ${VENDOR}/jquery \
    ${VENDOR}/d3 \
    ${VENDOR}/fonts

echo "- Installing JS/CSS"
curl -fsSL https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css -o ${VENDOR}/bootstrap/bootstrap.min.css
curl -fsSL https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js -o ${VENDOR}/bootstrap/bootstrap.bundle.min.js
curl -fsSL https://code.jquery.com/jquery-3.1.1.min.js -o ${VENDOR}/jquery/jquery-3.1.1.min.js
curl -fsSL https://cdnjs.cloudflare.com/ajax/libs/ace/1.35.3/ace.min.js -o ${VENDOR}/ace/ace.min.js
curl -fsSL https://cdnjs.cloudflare.com/ajax/libs/ace/1.43.2/mode-sql.min.js -o ${VENDOR}/ace/mode-sql.js
curl -fsSL https://cdnjs.cloudflare.com/ajax/libs/ace/1.43.2/theme-chrome.min.js -o ${VENDOR}/ace/theme-chrome.js
curl -fsSL https://cdnjs.cloudflare.com/ajax/libs/d3/7.9.0/d3.min.js -o ${VENDOR}/d3/d3.min.js
curl -fsSL https://cdnjs.cloudflare.com/ajax/libs/dagre-d3/0.6.4/dagre-d3.min.js -o ${VENDOR}/d3/dagre-d3.min.js

echo "- Installing fonts"
curl -fsSL https://cdn.jsdelivr.net/gh/deniskrumko/fonts@v1/fonts/zain/Zain-Bold.ttf -o ${VENDOR}/fonts/Zain-Bold.ttf
curl -fsSL https://cdn.jsdelivr.net/gh/deniskrumko/fonts@v1/fonts/zain/Zain-Regular.ttf -o ${VENDOR}/fonts/Zain-Regular.ttf

echo "Installed all vendor libraries!"
