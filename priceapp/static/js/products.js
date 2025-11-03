let productCount = 0;
      let priceCount = 0;
      let sizeCount = 0;
      let editingProductId = null;
      let allProducts = []; // Store all products for search functionality

      // Search functionality
      function searchProducts(searchTerm) {
        console.log(`🔍 Searching for: "${searchTerm}"`);
        
        const clearBtn = document.getElementById('clearSearchBtn');
        const clearBtnMobile = document.getElementById('clearSearchBtnMobile');
        
        // Sync both search boxes
        const searchBox = document.getElementById('searchBox');
        const searchBoxMobile = document.getElementById('searchBoxMobile');
        if (searchBox && searchBox.value !== searchTerm) searchBox.value = searchTerm;
        if (searchBoxMobile && searchBoxMobile.value !== searchTerm) searchBoxMobile.value = searchTerm;
        
        if (!searchTerm.trim()) {
          // If search is empty, show all products and hide clear buttons
          displayFilteredProducts(allProducts);
          if (clearBtn) clearBtn.style.display = 'none';
          if (clearBtnMobile) clearBtnMobile.style.display = 'none';
          
          // Hide search summary
          const searchSummary = document.getElementById('searchSummary');
          if (searchSummary) searchSummary.style.display = 'none';
          return;
        }
        
        // Show clear buttons when there's a search term
        if (clearBtn) clearBtn.style.display = 'block';
        if (clearBtnMobile) clearBtnMobile.style.display = 'block';
        
        const filtered = allProducts.filter(product => {
          // Search in product name
          const nameMatch = product.name?.toLowerCase().includes(searchTerm.toLowerCase());
          
          // Search in sizes
          const sizeMatch = product.sizes?.some(size => 
            size.size?.toLowerCase().includes(searchTerm.toLowerCase()) ||
            size.code?.toLowerCase().includes(searchTerm.toLowerCase()) ||
            size.hsn?.toLowerCase().includes(searchTerm.toLowerCase())
          );
          
          // Search in dealers
          const dealerMatch = product.sizes?.some(size => 
            size.prices?.some(price => 
              price.dealers?.some(dealer => 
                dealer.dlr_name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
                dealer.slol?.toLowerCase().includes(searchTerm.toLowerCase())
              )
            )
          );
          
          return nameMatch || sizeMatch || dealerMatch;
        });
        
        console.log(`✅ Found ${filtered.length} matching products`);
        displayFilteredProducts(filtered);
        
        // Show search results summary
        const searchSummary = document.getElementById('searchSummary');
        if (searchSummary) {
          if (filtered.length === 0) {
            searchSummary.textContent = `No results found for "${searchTerm}"`;
            searchSummary.className = 'text-muted small mb-2';
          } else {
            searchSummary.textContent = `Found ${filtered.length} product${filtered.length === 1 ? '' : 's'} matching "${searchTerm}"`;
            searchSummary.className = 'text-success small mb-2';
          }
          searchSummary.style.display = 'block';
        }
      }
      
      // Logout functionality
      function logout() {
        console.log('🚪 Logging out...');
        
        if (confirm('Are you sure you want to logout?')) {
          // Clear any unsaved data
          if (document.querySelectorAll('#productList tr[id^="product_"]').length > 0) {
            if (!confirm('You have unsaved products. Are you sure you want to logout and lose this data?')) {
              return;
            }
          }
          
          // Redirect to login page
          console.log('👋 Redirecting to login page...');
          window.location.href = '/login/';
        }
      }
      
      // Clear search functionality
      function clearSearch() {
        const searchBox = document.getElementById('searchBox');
        const searchBoxMobile = document.getElementById('searchBoxMobile');
        const clearBtn = document.getElementById('clearSearchBtn');
        const clearBtnMobile = document.getElementById('clearSearchBtnMobile');
        const searchSummary = document.getElementById('searchSummary');
        
        // Clear both search boxes
        if (searchBox) searchBox.value = '';
        if (searchBoxMobile) searchBoxMobile.value = '';
        
        // Hide both clear buttons
        if (clearBtn) clearBtn.style.display = 'none';
        if (clearBtnMobile) clearBtnMobile.style.display = 'none';
        
        // Hide search summary
        if (searchSummary) {
          searchSummary.style.display = 'none';
        }
        
        // Show all products
        displayFilteredProducts(allProducts);
        console.log('🔍 Search cleared - showing all products');
      }

      function createInput(
        type = "text",
        value = "",
        classes = "form-control",
        extra = ""
      ) {
        return `<input type="${type}" class="${classes}" value="${value}" ${extra}>`;
      }

      function calc(value, percent) {
        const v = parseFloat(value || 0);
        const p = parseFloat(percent || 0);
        return ((v * p) / 100).toFixed(2);
      }

      // Helper function to convert file to base64
      // function fileToBase64(file) {
      //   return new Promise((resolve, reject) => {
      //     const reader = new FileReader();
      //     reader.readAsDataURL(file);
      //     reader.onload = () => resolve(reader.result);
      //     reader.onerror = error => reject(error);
      //   });
      // }

      // --- Base64 and resize logic for photo upload is DISABLED for PythonAnywhere free ---
      // Use standard file upload to Django media instead. Do NOT convert images to base64 or resize in JS.
      // The backend should handle file uploads via multipart/form-data.

      // Preview selected photo
      function previewPhoto(input) {
        const file = input.files[0];
        const previewDiv = input.parentElement.querySelector('.photo-preview');
        const previewImg = previewDiv.querySelector('img');
        
        if (file) {
          const reader = new FileReader();
          reader.onload = function(e) {
            previewImg.src = e.target.result;
            previewDiv.style.display = 'block';
            console.log(`📷 New photo preview loaded: ${file.name}`);
            
            // Dim existing photo preview if in edit mode
            const existingPreview = input.parentElement.querySelector('.existing-photo-preview');
            if (existingPreview && !existingPreview.getAttribute('data-remove-photo')) {
              existingPreview.style.opacity = '0.5';
              const infoDiv = existingPreview.querySelector('div:nth-child(2) > div:nth-child(2)');
              if (infoDiv) {
                infoDiv.textContent = 'Will be replaced';
                infoDiv.className = 'text-warning';
              }
            }
          };
          reader.readAsDataURL(file);
        } else {
          previewDiv.style.display = 'none';
          previewImg.src = '';
          
          // Restore existing photo preview if in edit mode  
          const existingPreview = input.parentElement.querySelector('.existing-photo-preview');
          if (existingPreview && !existingPreview.getAttribute('data-remove-photo')) {
            existingPreview.style.opacity = '1';
            const infoDiv = existingPreview.querySelector('div:nth-child(2) > div:nth-child(2)');
            if (infoDiv) {
              infoDiv.textContent = 'Select new or keep current';
              infoDiv.className = 'text-info';
            }
          }
        }
      }

      // Clear photo preview for new photos
      function clearPhotoPreview(button) {
        const photoCell = button.closest('td');
        const fileInput = photoCell.querySelector('input[type="file"]');
        const previewDiv = photoCell.querySelector('.photo-preview');
        
        if (fileInput) {
          fileInput.value = '';
          previewDiv.style.display = 'none';
          
          // Trigger the preview function to restore existing photo state
          previewPhoto(fileInput);
        }
      }

      // Toggle save button visibility based on product rows
      function toggleSaveButtonVisibility() {
        const productRows = document.querySelectorAll('#productList tr[id^="product_"]');
        const saveBtn = document.getElementById("saveProductsBtn");
        
        if (productRows.length > 0) {
          saveBtn.style.display = 'block';
        } else {
          saveBtn.style.display = 'none';
        }
      }

      // Remove product row and toggle save button visibility
      function removeProductRow(button, productId) {
        // Remove the product row and all related rows
        const productRow = document.getElementById(`product_${productId}`);
        const allRelatedRows = document.querySelectorAll(`tr[class*="product_${productId}"]`);
        
        // Remove all related rows (sizes, prices, dealers)
        allRelatedRows.forEach(row => row.remove());
        
        // Remove the main product row
        if (productRow) {
          productRow.remove();
        }
        
        // Update save button visibility
        toggleSaveButtonVisibility();
      }

      // Remove current photo during edit
      function removeCurrentPhoto(button) {
        const photoCell = button.closest('td');
        const existingPreview = photoCell.querySelector('.existing-photo-preview');
        const fileInput = photoCell.querySelector('input[type="file"]');
        
        if (existingPreview) {
          // Replace the preview with a removal indicator
          existingPreview.innerHTML = `
            <div style="display: flex; align-items: center; gap: 8px; margin-top: 4px; padding: 8px; background-color: #fff3cd; border: 1px solid #ffeaa7; border-radius: 4px;">
              <div style="width: 40px; height: 40px; display: flex; align-items: center; justify-content: center; background-color: #f8f9fa; border: 1px dashed #dee2e6; border-radius: 4px; color: #6c757d; font-size: 18px;">✕</div>
              <div style="flex: 1; font-size: 12px;">
                <div class="text-warning"><strong>Photo will be removed</strong></div>
                <div class="text-muted">Photo will be deleted when you update</div>
              </div>
              <button type="button" class="btn btn-sm btn-outline-secondary" onclick="undoRemovePhoto(this)" title="Undo remove photo" style="padding: 2px 6px; font-size: 10px;">↶</button>
            </div>
          `;
          
          // Mark for removal by adding a special attribute
          existingPreview.setAttribute('data-remove-photo', 'true');
          console.log('📷 Current photo marked for removal');
        }
      }

      // Undo photo removal
      function undoRemovePhoto(button) {
        const photoCell = button.closest('td');
        const existingPreview = photoCell.querySelector('.existing-photo-preview');
        
        // Get the original photo URL from the current product being edited
        fetch(`/api/product-create/`)
          .then(res => res.json())
          .then(products => {
            const product = products.find(p => p.id === editingProductId);
            if (product && product.photo && existingPreview) {
              // Restore the original preview
              existingPreview.innerHTML = `
                <div style="display: flex; align-items: center; gap: 8px; margin-top: 4px;">
                  <img src="${product.photo}" alt="Current Photo" style="width: 40px; height: 40px; object-fit: cover; border: 1px solid #ddd; border-radius: 4px; flex-shrink: 0;">
                  <div style="flex: 1; font-size: 12px;">
                    <div class="text-muted">Current photo</div>
                    <div class="text-info">Select new or keep current</div>
                  </div>
                  <button type="button" class="btn btn-sm btn-outline-danger" onclick="removeCurrentPhoto(this)" title="Remove current photo" style="padding: 2px 6px; font-size: 10px;">✕</button>
                </div>
              `;
              
              // Remove the removal marker
              existingPreview.removeAttribute('data-remove-photo');
              console.log('📷 Photo removal undone');
            }
          })
          .catch(err => console.error('Error restoring photo preview:', err));
      }

      // --- Add Dealer Row ---
      function addDealerRow(priceRow, productId, sizeId, priceId) {
        const dealerRow = document.createElement("tr");
        dealerRow.classList.add(
          `product_${productId}_size_${sizeId}_price_${priceId}_dealer`
        );

        dealerRow.innerHTML = `
        <td colspan="13"></td>
        <td>${createInput("text", "", "form-control", 'placeholder="Dealer"')}</td>
        <td>${createInput("text", "", "form-control", 'placeholder="SLOL"')}</td>
        <td>${createInput("date", "", "form-control", 'onclick="this.showPicker();"')}</td>
        <td>${createInput(
          "number",
          "",
          "form-control",
          'placeholder="Price" oninput="updateDealerCalc(this)"'
        )}</td>
        <td>
          <div>${createInput("number", "", "form-control", 'placeholder="%" oninput="updateDealerCalc(this)"')}</div>
          <small class="text-muted">₹${createInput("number", "", "form-control readonly-field", 'readonly tabindex="-1" style="font-size:10px;height:20px;"')}</small>
        </td>
        <td>
          <div>${createInput("number", "", "form-control", 'placeholder="%" oninput="updateDealerCalc(this)"')}</div>
          <small class="text-muted">₹${createInput("number", "", "form-control readonly-field", 'readonly tabindex="-1" style="font-size:10px;height:20px;"')}</small>
        </td>
        <td>${createInput(
          "number",
          "",
          "form-control",
          'oninput="updateDealerCalc(this)"'
        )}</td>
        <td>
          <div>${createInput("number", "", "form-control", 'placeholder="%" oninput="updateDealerCalc(this)"')}</div>
          <small class="text-muted">₹${createInput("number", "", "form-control readonly-field", 'readonly tabindex="-1" style="font-size:10px;height:20px;"')}</small>
        </td>
        <td>
          <div>${createInput("number", "", "form-control", 'placeholder="%" oninput="updateDealerCalc(this)"')}</div>
          <small class="text-muted">₹${createInput("number", "", "form-control readonly-field", 'readonly tabindex="-1" style="font-size:10px;height:20px;"')}</small>
        </td>    
        <td>
          <button class="btn btn-sm btn-danger" onclick="this.closest('tr').remove()">🗑</button>
        </td>
        `;

        const existingDealers = document.querySelectorAll(
          `.product_${productId}_size_${sizeId}_price_${priceId}_dealer`
        );
        const insertAfter = existingDealers.length
          ? existingDealers[existingDealers.length - 1]
          : priceRow;
        insertAfter.parentNode.insertBefore(dealerRow, insertAfter.nextSibling);
      }

      // --- Add Price Row ---
      function addPriceRow(productId, sizeId) {
        const priceId = priceCount++;
        const priceRow = document.createElement("tr");
        priceRow.classList.add(`product_${productId}_size_${sizeId}_price`);
        priceRow.dataset.priceId = priceId;

        priceRow.innerHTML = `
        <td colspan="6"></td>
        <td>
          <select class="form-control">
            <option value="">Select Payment Type</option>
            <option value="cash">Cash</option>
            <option value="bill">Bill</option>
            <option value="sale_cash">Sale Cash</option>
            <option value="sale_bill">Sale Bill</option>
            <option value="frd_cash">Frd Cash</option>
            <option value="frd_bill">Frd Bill</option>
          </select>
        </td>
        <td>${createInput("number", "", "form-control", 'placeholder="Price" oninput="updatePriceCalc(this)"')}</td>
        <td>
          <div>${createInput("number", "", "form-control", 'placeholder="%" oninput="updatePriceCalc(this)"')}</div>
          <small class="text-muted">₹${createInput("number", "", "form-control readonly-field", 'readonly tabindex="-1" style="font-size:10px;height:20px;"')}</small>
        </td>
        <td>
          <div>${createInput("number", "", "form-control", 'placeholder="%" oninput="updatePriceCalc(this)"')}</div>
          <small class="text-muted">₹${createInput("number", "", "form-control readonly-field", 'readonly tabindex="-1" style="font-size:10px;height:20px;"')}</small>
        </td>
        <td>${createInput(
          "number",
          "",
          "form-control",
          'oninput="updatePriceCalc(this)"'
        )}</td>
        <td>
          <div>${createInput("number", "", "form-control", 'placeholder="%" oninput="updatePriceCalc(this)"')}</div>
          <small class="text-muted">₹${createInput("number", "", "form-control readonly-field", 'readonly tabindex="-1" style="font-size:10px;height:20px;"')}</small>
        </td>
        <td>
          <div>${createInput("number", "", "form-control", 'placeholder="%" oninput="updatePriceCalc(this)"')}</div>
          <small class="text-muted">₹${createInput("number", "", "form-control readonly-field", 'readonly tabindex="-1" style="font-size:10px;height:20px;"')}</small>
        </td>
        <td colspan="10">
          <button class="btn btn-sm btn-info" onclick="addDealerRow(this.closest('tr'),${productId},${sizeId},${priceId})">+ Deal</button>
          <button class="btn btn-sm btn-danger" onclick="this.closest('tr').remove()">🗑</button>
        </td>
        `;

        // Improved insertion logic: find the target size row and insert after the last related row
        const targetSizeRow = Array.from(document.querySelectorAll(`tr`)).find(row => 
          row.classList.contains(`product_${productId}_size`) && 
          row.dataset.sizeId == sizeId
        );
        
        if (targetSizeRow) {
          // Find all existing price and dealer rows for this size
          const allRelatedRows = Array.from(document.querySelectorAll(`tr`)).filter(row => 
            row.classList.toString().includes(`product_${productId}_size_${sizeId}`)
          );
          
          // Insert after the last related row, or after the size row if no related rows exist
          const insertAfter = allRelatedRows.length > 0 ? allRelatedRows[allRelatedRows.length - 1] : targetSizeRow;
          insertAfter.insertAdjacentElement('afterend', priceRow);
        } else {
          // Fallback: insert after product row
          const productRow = document.getElementById(`product_${productId}`);
          productRow.insertAdjacentElement('afterend', priceRow);
        }
      }

      // --- Add Size Row ---
      function addSizeRow(productId) {
        const sizeId = sizeCount++;
        const sizeRow = document.createElement("tr");
        sizeRow.classList.add(`product_${productId}_size`);
        sizeRow.dataset.sizeId = sizeId;
        sizeRow.innerHTML = `
          <td colspan="2"></td>
          <td>${createInput("text", "", "form-control", 'placeholder="Size"')}</td>
          <td>${createInput("text", "", "form-control", 'placeholder="Code"')}</td>
          <td>${createInput("text", "", "form-control", 'placeholder="HSN"')}</td>
          <td>${createInput("number", "", "form-control", 'placeholder="MRP" step="0.01"')}</td>
          <td colspan="17">
            <button class="btn btn-sm btn-success" onclick="addPriceRow(${productId},${sizeId})">+ Price</button>
            <button class="btn btn-sm btn-secondary" onclick="this.closest('tr').remove()">✖ Del</button>
          </td>
        `;
        const productRow = document.getElementById(`product_${productId}`);
        
        // Find all existing rows related to this product and insert after the last one
        const allProductRelatedRows = Array.from(document.querySelectorAll(`tr`)).filter(row => 
          row.classList.toString().includes(`product_${productId}`) && row.id !== `product_${productId}`
        );
        
        if (allProductRelatedRows.length > 0) {
          // Insert after the last related row
          const lastRelatedRow = allProductRelatedRows[allProductRelatedRows.length - 1];
          lastRelatedRow.insertAdjacentElement('afterend', sizeRow);
        } else {
          // Insert right after the product row if no related rows exist
          productRow.insertAdjacentElement('afterend', sizeRow);
        }
      }

      // --- Add Product Row ---
      function addProductRow() {
        const tbody = document.getElementById("productList");
        const productId = productCount++;
        const productRow = document.createElement("tr");
        productRow.id = `product_${productId}`;
        productRow.innerHTML = `
        <td>
          ${createInput("file", "", "form-control", 'accept="image/*" onchange="previewPhoto(this)"')}
          <div class="photo-preview mt-1" style="display:none;">
            <div style="display: flex; align-items: center; gap: 8px;">
              <img style="width: 40px; height: 40px; object-fit: cover; border: 1px solid #ddd; border-radius: 4px; flex-shrink: 0;">
              <div style="flex: 1; font-size: 12px;">
                <div class="text-success">New photo selected</div>
              </div>
              <button type="button" class="btn btn-sm btn-outline-secondary" onclick="clearPhotoPreview(this)" title="Clear photo" style="padding: 2px 6px; font-size: 10px;">✕</button>
            </div>
          </div>
        </td>
        <td>${createInput("text")}</td>
        <td colspan="21">
          <button class="btn btn-sm btn-success" onclick="addSizeRow(${productId})">+ Size</button>
          <button class="btn btn-sm btn-secondary" onclick="removeProductRow(this, ${productId})">✖ Del</button>
        </td>
      `;
        if (tbody.firstChild) {
          tbody.insertBefore(productRow, tbody.firstChild);
        } else {
          tbody.appendChild(productRow);
        }
        // Show save button when product is added
        toggleSaveButtonVisibility();

        // Scroll to the new row (top of list)
        setTimeout(() => {
          productRow.scrollIntoView({ behavior: 'smooth', block: 'start' });
          // Adjust scroll to account for sticky header (header height ~56px)
          const headerOffset = 90; // Increase offset for sticky header height
          const scroller = document.querySelector('.table-responsive') || window;
          const rowRect = productRow.getBoundingClientRect();
          const scrollerRect = scroller.getBoundingClientRect ? scroller.getBoundingClientRect() : { top: 0 };
          const scrollTop = (scroller === window ? window.scrollY : scroller.scrollTop);
          const offset = rowRect.top - scrollerRect.top - headerOffset;
          if (scroller === window) {
            window.scrollTo({ top: scrollTop + offset, behavior: 'smooth' });
          } else {
            scroller.scrollTo({ top: scrollTop + offset, behavior: 'smooth' });
          }
          // Focus the product name input (second cell, first input)
          const nameInput = productRow.querySelectorAll('td')[1]?.querySelector('input');
          if (nameInput) nameInput.focus();
        }, 100);
      }

      // --- Price Calculations ---
      function updatePriceCalc(element) {
        const row = element.closest("tr");
        const cells = row.querySelectorAll("td");
        
        // Get values from specific cells by position
        const priceInput = cells[2]?.querySelector("input"); // Price column
        const discountPercentInput = cells[3]?.querySelector("div input"); // Discount % input
        const discountPriceInput = cells[3]?.querySelector("small input"); // Discount price display
        const taxPercentInput = cells[4]?.querySelector("div input"); // Tax % input  
        const taxPriceInput = cells[4]?.querySelector("small input"); // Tax price display
        
        const price = parseFloat(priceInput?.value || 0);
        const discountPercent = parseFloat(discountPercentInput?.value || 0);
        const taxPercent = parseFloat(taxPercentInput?.value || 0);
        
        const discountAmount = parseFloat(calc(price, discountPercent));
        const priceAfterDiscount = price - discountAmount;
        const taxAmount = parseFloat(calc(priceAfterDiscount, taxPercent));
        const finalTotal = priceAfterDiscount + taxAmount;
        
        // Show final price after discount in the small field under discount %
        if (discountPriceInput) {
          discountPriceInput.value = priceAfterDiscount.toFixed(2);
          console.log(`✅ Discount calculation: ${price} - ${discountPercent}% = ₹${priceAfterDiscount.toFixed(2)}`);
        }
        // Show final price after tax in the small field under tax %
        if (taxPriceInput) {
          taxPriceInput.value = finalTotal.toFixed(2);
          console.log(`✅ Tax calculation: ₹${priceAfterDiscount.toFixed(2)} + ${taxPercent}% tax = ₹${finalTotal.toFixed(2)}`);
        }
        
        console.log(`🔍 Full calculation: Price: ${price}, Discount: ${discountPercent}% (₹${discountAmount}), Final after discount: ₹${priceAfterDiscount.toFixed(2)}, Tax: ${taxPercent}% (₹${taxAmount}), Final total: ₹${finalTotal.toFixed(2)}`);

        // Box calculations
        const boxQtyInput = cells[5]?.querySelector("input"); // Box quantity column
        const boxDiscountPercentInput = cells[6]?.querySelector("div input"); // Box Discount % input
        const boxDiscountPriceInput = cells[6]?.querySelector("small input"); // Box discount price display
        const boxTaxPercentInput = cells[7]?.querySelector("div input"); // Box Tax % input  
        const boxTaxPriceInput = cells[7]?.querySelector("small input"); // Box tax price display
        
        const boxQty = parseFloat(boxQtyInput?.value || 0);
        const boxDiscountPercent = parseFloat(boxDiscountPercentInput?.value || 0);
        const boxTaxPercent = parseFloat(boxTaxPercentInput?.value || 0);
        
        if (boxQty > 0) {
          const boxPrice = price * boxQty;
          const boxDiscountAmount = parseFloat(calc(boxPrice, boxDiscountPercent));
          const boxPriceAfterDiscount = boxPrice - boxDiscountAmount;
          const boxTaxAmount = parseFloat(calc(boxPriceAfterDiscount, boxTaxPercent));
          const boxFinalTotal = boxPriceAfterDiscount + boxTaxAmount;
          
          // Show final box price after discount
          if (boxDiscountPriceInput) boxDiscountPriceInput.value = boxPriceAfterDiscount.toFixed(2);
          // Show final box price after tax
          if (boxTaxPriceInput) boxTaxPriceInput.value = boxFinalTotal.toFixed(2);
        }
      }

      // --- Dealer Calculations ---
      function updateDealerCalc(element) {
        const row = element.closest("tr");
        const cells = row.querySelectorAll("td");
        
        // Dealer row structure: colspan="13", then dealer_name, slol, date, price, discount, tax, box, box_discount, box_tax, actions
        // So actual inputs start at index 1 (after the colspan)
        const dealerPriceInput = cells[4]?.querySelector("input"); // Dealer Price column (4th cell after colspan)
        const dealerDiscountPercentInput = cells[5]?.querySelector("div input"); // Dealer Discount % input
        const dealerDiscountPriceInput = cells[5]?.querySelector("small input"); // Dealer discount price display
        const dealerTaxPercentInput = cells[6]?.querySelector("div input"); // Dealer Tax % input  
        const dealerTaxPriceInput = cells[6]?.querySelector("small input"); // Dealer tax price display
        
        const purchasePrice = parseFloat(dealerPriceInput?.value || 0);
        const purchaseDiscountPercent = parseFloat(dealerDiscountPercentInput?.value || 0);
        const purchaseTaxPercent = parseFloat(dealerTaxPercentInput?.value || 0);
        
        const purchaseDiscountAmount = parseFloat(calc(purchasePrice, purchaseDiscountPercent));
        const purchasePriceAfterDiscount = purchasePrice - purchaseDiscountAmount;
        const purchaseTaxAmount = parseFloat(calc(purchasePriceAfterDiscount, purchaseTaxPercent));
        const purchaseFinalTotal = purchasePriceAfterDiscount + purchaseTaxAmount;
        
        // Show final price after discount in the small field under discount %
        if (dealerDiscountPriceInput) {
          dealerDiscountPriceInput.value = purchasePriceAfterDiscount.toFixed(2);
          console.log(`✅ Dealer Discount: ${purchasePrice} - ${purchaseDiscountPercent}% = ₹${purchasePriceAfterDiscount.toFixed(2)}`);
        }
        // Show final price after tax in the small field under tax %
        if (dealerTaxPriceInput) {
          dealerTaxPriceInput.value = purchaseFinalTotal.toFixed(2);
          console.log(`✅ Dealer Tax: ₹${purchasePriceAfterDiscount.toFixed(2)} + ${purchaseTaxPercent}% tax = ₹${purchaseFinalTotal.toFixed(2)}`);
        }

        // Purchase box calculations
        const dealerBoxQtyInput = cells[7]?.querySelector("input"); // Dealer Box quantity column
        const dealerBoxDiscountPercentInput = cells[8]?.querySelector("div input"); // Dealer Box Discount % input
        const dealerBoxDiscountPriceInput = cells[8]?.querySelector("small input"); // Dealer box discount price display
        const dealerBoxTaxPercentInput = cells[9]?.querySelector("div input"); // Dealer Box Tax % input  
        const dealerBoxTaxPriceInput = cells[9]?.querySelector("small input"); // Dealer box tax price display
        
        const purchaseBoxQty = parseFloat(dealerBoxQtyInput?.value || 0);
        const purchaseBoxDiscountPercent = parseFloat(dealerBoxDiscountPercentInput?.value || 0);
        const purchaseBoxTaxPercent = parseFloat(dealerBoxTaxPercentInput?.value || 0);
        
        if (purchaseBoxQty > 0) {
          const purchaseBoxPrice = purchasePrice * purchaseBoxQty;
          const purchaseBoxDiscountAmount = parseFloat(calc(purchaseBoxPrice, purchaseBoxDiscountPercent));
          const purchaseBoxPriceAfterDiscount = purchaseBoxPrice - purchaseBoxDiscountAmount;
          const purchaseBoxTaxAmount = parseFloat(calc(purchaseBoxPriceAfterDiscount, purchaseBoxTaxPercent));
          const purchaseBoxFinalTotal = purchaseBoxPriceAfterDiscount + purchaseBoxTaxAmount;
          
          // Show final box price after discount
          if (dealerBoxDiscountPriceInput) dealerBoxDiscountPriceInput.value = purchaseBoxPriceAfterDiscount.toFixed(2);
          // Show final box price after tax
          if (dealerBoxTaxPriceInput) dealerBoxTaxPriceInput.value = purchaseBoxFinalTotal.toFixed(2);
        }
      }


            document
        .getElementById("saveProductsBtn")
        .addEventListener("click", () => {
          const data = [];
          const productRows = document.querySelectorAll(
            '#productList tr[id^="product_"]'
          );

          productRows.forEach((pRow) => {
            const productId = pRow.id.split("_")[1];
            const productInputs = pRow.querySelectorAll("input");
            
            // Create Product data
            const productData = {
              name: productInputs[1]?.value || "",
              sizes: []
            };
            
            // Handle photo based on current state
            const photoFile = productInputs[0]?.files?.[0];
            const photoCell = productInputs[0]?.closest('td');
            const existingPreview = photoCell?.querySelector('.existing-photo-preview');
            const isMarkedForRemoval = existingPreview?.getAttribute('data-remove-photo') === 'true';
            
            if (photoFile) {
              // New photo selected
              productData.photo = photoFile;
              console.log(`📷 New photo detected: ${photoFile.name}, Size: ${photoFile.size} bytes, Type: ${photoFile.type}`);
            } else if (isMarkedForRemoval) {
              // Photo marked for removal
              productData.removePhoto = true;
              console.log(`📷 Photo marked for removal for product: ${productData.name}`);
            } else {
              // No change to photo
              console.log(`📷 No photo change for product: ${productData.name}`);
            }
            
            // Debug: Log the current state
            console.log(`📷 Photo collection debug - File: ${!!photoFile}, Marked for removal: ${isMarkedForRemoval}, Has photo field: ${'photo' in productData}, Has removePhoto flag: ${!!productData.removePhoto}`);
            
            if (productData.photo && typeof productData.photo !== 'object') {
              console.error(`❌ Invalid photo data type: ${typeof productData.photo}`, productData.photo);
            }

            // Get all size rows for this product
            const sizeRows = document.querySelectorAll(`.product_${productId}_size`);
            sizeRows.forEach(sizeRow => {
              const sizeId = sizeRow.dataset.sizeId;
              const sizeInputs = sizeRow.querySelectorAll("input");
              const sizeData = {
                size: sizeInputs[0]?.value || "",
                code: sizeInputs[1]?.value || "",
                hsn: sizeInputs[2]?.value || "",
                mrp: parseFloat(sizeInputs[3]?.value || 0),
                prices: [] // Prices now belong to ProductSize
              };

              // Get all price rows for this specific size
              const priceRows = document.querySelectorAll(`.product_${productId}_size_${sizeId}_price`);
              priceRows.forEach(priceRow => {
                const priceId = priceRow.dataset.priceId;
                const priceInputs = priceRow.querySelectorAll("input, select");
                const priceData = {
                  payment_type: priceInputs[0]?.value || "",
                  price: parseFloat(priceInputs[1]?.value || 0),
                  discount: parseFloat(priceInputs[2]?.value || 0),
                  discount_price: parseFloat(priceInputs[3]?.value || 0),
                  tax: parseFloat(priceInputs[4]?.value || 0),
                  tax_price: parseFloat(priceInputs[5]?.value || 0),
                  box: parseFloat(priceInputs[6]?.value || 0),
                  box_discount: parseFloat(priceInputs[7]?.value || 0),
                  box_discount_price: parseFloat(priceInputs[8]?.value || 0),
                  box_tax: parseFloat(priceInputs[9]?.value || 0),
                  box_tax_price: parseFloat(priceInputs[10]?.value || 0),
                  dealers: []
                };
                
                console.log(`💾 Saving price data: Price=${priceData.price}, Discount=${priceData.discount}%, Discount_Price=₹${priceData.discount_price}, Tax=${priceData.tax}%, Tax_Price=₹${priceData.tax_price}`);

                // Get dealer rows for this price
                const dealerRows = document.querySelectorAll(`.product_${productId}_size_${sizeId}_price_${priceId}_dealer`);
                dealerRows.forEach(dealerRow => {
                  const dealerInputs = dealerRow.querySelectorAll("input");
                  const dealerData = {
                    dlr_name: dealerInputs[0]?.value || "",
                    slol: dealerInputs[1]?.value || "",
                    purchase_date: dealerInputs[2]?.value || "",
                    purchase_price: parseFloat(dealerInputs[3]?.value || 0),
                    purchase_discount: parseFloat(dealerInputs[4]?.value || 0),
                    purchase_discount_price: parseFloat(dealerInputs[5]?.value || 0),
                    purchase_tax: parseFloat(dealerInputs[6]?.value || 0),
                    purchase_tax_price: parseFloat(dealerInputs[7]?.value || 0),
                    purchase_box: parseFloat(dealerInputs[8]?.value || 0),
                    purchase_box_discount: parseFloat(dealerInputs[9]?.value || 0),
                    purchase_box_discount_price: parseFloat(dealerInputs[10]?.value || 0),
                    purchase_box_tax: parseFloat(dealerInputs[11]?.value || 0),
                    purchase_box_tax_price: parseFloat(dealerInputs[12]?.value || 0)
                  };
                  priceData.dealers.push(dealerData);
                });

                sizeData.prices.push(priceData);
              });

              productData.sizes.push(sizeData);
            });

            data.push(productData);
          });

          console.log("✅ Final Data:", JSON.stringify(data, null, 2));

          // Check if we're in edit mode
          if (editingProductId) {
            // Update mode - send PUT request for single product
            if (data.length > 0) {
              const productData = data[0]; // Only update the first product
              updateProduct(editingProductId, productData);
            }
          } else {
            // Create mode - send POST requests for all products
            saveAllProducts(data);
          }
        });

      // Save all products function with proper async handling
      async function saveAllProducts(data) {
        let successCount = 0;
        let errorCount = 0;
        const totalProducts = data.length;
        
        console.log(`💾 Starting to save ${totalProducts} products...`);
        
        // Show loading state
        const saveBtn = document.getElementById("saveProductsBtn");
        const originalText = saveBtn.textContent;
        saveBtn.textContent = "💾 Saving...";
        saveBtn.disabled = true;
        
        try {
          // Use Promise.all to wait for all saves to complete
          const savePromises = data.map(async (productData, index) => {
            try {
              // --- Base64/resize logic DISABLED ---
              // Use standard file upload for productData.photo (File object)
              // The backend should accept multipart/form-data for image uploads.
              // If photo is present, keep as File; do not convert to base64.
              if (productData.photo && productData.photo instanceof File) {
                // Leave productData.photo as File; handle upload in backend
              } else if (productData.removePhoto) {
                delete productData.photo;
                delete productData.removePhoto;
              }
              
              // Debug: Log the final photo value being sent for creation
              if ('photo' in productData) {
                console.log(`📷 Final photo value for creation - type: ${typeof productData.photo}`);
              } else {
                console.log(`📷 Photo field not included in creation data`);
              }
              
              // Use FormData for file upload
              const formData = new FormData();
              for (const key in productData) {
                formData.append(key, productData[key]);
              }
              const response = await fetch("/api/product-create/", {
                method: "POST",
                headers: {
                  "X-CSRFToken": getCookie("csrftoken"),
                },
                body: formData,
              });
              
              const result = await response.json();
              
              if (response.ok) {
                console.log(`✅ Product ${index + 1} saved successfully:`, result);
                successCount++;
                return result;
              } else {
                console.error(`❌ Error saving product ${index + 1}:`, result);
                errorCount++;
                throw new Error(`Product ${index + 1}: ${JSON.stringify(result)}`);
              }
            } catch (err) {
              console.error(`❌ Network error for product ${index + 1}:`, err);
              errorCount++;
              throw err;
            }
          });
          
          // Wait for all save operations to complete
          await Promise.allSettled(savePromises);
          
          // Show results and refresh
          if (successCount > 0) {
            console.log(`✅ Successfully saved ${successCount} out of ${totalProducts} products!`);
            
            // Show brief success indication on button
            saveBtn.textContent = "✅ Saved!";
            saveBtn.className = "btn btn-success mt-2 w-100";
            
            // Clear the form after a brief delay
            setTimeout(() => {
              document.getElementById('productList').innerHTML = '';
              productCount = 0;
              sizeCount = 0;
              priceCount = 0;
              
              // Hide save button after clearing form
              toggleSaveButtonVisibility();
              
              // Refresh the product display
              displayProductsWithNestedStructure();
              
              console.log(`🔄 Page refreshed to show new products`);
            }, 1000);
          }
          
          if (errorCount > 0) {
            console.log(`⚠️ ${errorCount} products failed to save. Check console for details.`);
          }
          
        } catch (err) {
          console.error('❌ Unexpected error during save operation:', err);
        } finally {
          // Restore button state
          saveBtn.textContent = originalText;
          saveBtn.disabled = false;
        }
      }

      // Update product function
      async function updateProduct(productId, productData) {
        console.log(`🔧 Updating product ID: ${productId}`);
        console.log(`📝 Product data:`, productData);
        
        try {
          const url = `/api/product-create/${productId}/`;
          console.log(`📡 Sending PATCH request to: ${url}`);
          
          // --- Base64/resize logic DISABLED for update ---
          // Use standard file upload for productData.photo (File object)
          if (productData.photo && productData.photo instanceof File) {
            // Leave productData.photo as File; handle upload in backend
          } else if (productData.removePhoto) {
            productData.photo = "";
            delete productData.removePhoto;
          } else {
            delete productData.photo;
          }
          
          // Debug: Log the final photo value being sent
          if ('photo' in productData) {
            console.log(`📷 Final photo value type: ${typeof productData.photo}`);
          } else {
            console.log(`📷 Photo field not included in update data`);
          }
          
          // Use FormData for file upload
          const formData = new FormData();
          for (const key in productData) {
            formData.append(key, productData[key]);
          }
          const response = await fetch(url, {
            method: "PATCH",
            headers: {
              "X-CSRFToken": getCookie("csrftoken"),
            },
            body: formData,
          });
          
          console.log(`📡 Response status: ${response.status}`);
          console.log(`📡 Response headers:`, response.headers);
          
          const result = await response.json();
          console.log(`📋 Response data:`, result);
          
          if (response.ok) {
            console.log(`✅ Product updated successfully!`);
            
            // Reset edit mode UI
            cancelEdit();
            
            // Reload the product list
            window.location.reload();
          } else {
            console.error(`❌ Error response status: ${response.status}`);
            console.error(`❌ Error response body:`, result);
          }
        } catch (err) {
          console.error(`❌ Network error updating product:`, err);
        }
      }

      // Cancel edit mode function
      function cancelEdit() {
        editingProductId = null;
        document.getElementById("saveProductsBtn").textContent = "💾 Save Products";
        document.getElementById("saveProductsBtn").className = "btn btn-success mt-2 w-100";
        document.getElementById("cancelEditBtn").style.display = "none";
        document.getElementById('productList').innerHTML = '';
        productCount = 0;
        sizeCount = 0;
        priceCount = 0;
        console.log("✅ Edit mode cancelled");
        
        // Hide save button when clearing form
        toggleSaveButtonVisibility();
        
        // Refresh page to show product list
        displayProductsWithNestedStructure();
      }

      // Delete product function
      async function deleteProduct(productId) {
        console.log(`🗑️ Attempting to delete product ID: ${productId}`);
        
        // Get product name for better confirmation message
        let productName = "this product";
        try {
          const productRow = document.querySelector(`button[onclick="deleteProduct(${productId})"]`);
          if (productRow) {
            const nameCell = productRow.closest('tr').querySelector('td:nth-child(2)');
            if (nameCell && nameCell.textContent.trim()) {
              productName = `"${nameCell.textContent.trim()}"`;
            }
          }
        } catch (e) {
          // Fallback to generic message if we can't get the name
        }
        
        if (!confirm(`Are you sure you want to delete ${productName}?\n\nThis action cannot be undone and will remove all associated sizes, prices, and dealer information.`)) {
          console.log("❌ Delete cancelled by user");
          return;
        }
        
        // Find and disable all delete buttons temporarily
        const deleteButtons = document.querySelectorAll(`button[onclick="deleteProduct(${productId})"]`);
        deleteButtons.forEach(btn => {
          btn.disabled = true;
          btn.textContent = "🗑 Deleting...";
        });
        
        try {
          const url = `/api/product-create/${productId}/`;
          console.log(`📡 Sending DELETE request to: ${url}`);
          
          const response = await fetch(url, {
            method: "DELETE",
            headers: {
              "X-CSRFToken": getCookie("csrftoken"),
            },
          });
          
          console.log(`📡 Delete response status: ${response.status}`);
          
          if (response.ok) {
            console.log("✅ Product deleted successfully!");
            
            // Refresh the product display instead of full page reload
            displayProductsWithNestedStructure();
            console.log("🔄 Product list refreshed after deletion");
          } else {
            const result = await response.json();
            console.error(`❌ Error deleting product (${response.status}):`, result);
            
            // Restore button state on error
            deleteButtons.forEach(btn => {
              btn.disabled = false;
              btn.textContent = "🗑 Delete";
            });
          }
        } catch (err) {
          console.error("❌ Network error deleting product:", err);
          
          // Restore button state on error
          deleteButtons.forEach(btn => {
            btn.disabled = false;
            btn.textContent = "🗑 Delete";
          });
        }
      }

      function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== "") {
          const cookies = document.cookie.split(";");
          for (let cookie of cookies) {
            cookie = cookie.trim();
            if (cookie.startsWith(name + "=")) {
              cookieValue = decodeURIComponent(
                cookie.substring(name.length + 1)
              );
              break;
            }
          }
        }
        return cookieValue;
      }
      // Removed old incorrect display function

      // Override the display function to handle nested structure correctly
      function displayProductsWithNestedStructure() {
        fetch("/api/product-create/")
          .then((res) => res.json())
          .then((data) => {
            // Store all products globally for search functionality
            allProducts = data;
            console.log(`📦 Loaded ${allProducts.length} products for search`);
            
            // Display all products initially
            displayFilteredProducts(data);
          })
          .catch((err) => console.error("Error loading products:", err));
      }
      
      // Display filtered products (used by both main display and search)
      function displayFilteredProducts(data) {
        const tbody = document.getElementById("productList");
        tbody.innerHTML = ""; // clear old
        
        if (data.length === 0) {
          const noResultsRow = document.createElement("tr");
          noResultsRow.innerHTML = `
            <td colspan="23" class="text-center text-muted py-4">
              <div>🔍 No products found</div>
              <small>Try adjusting your search terms</small>
            </td>
          `;
          tbody.appendChild(noResultsRow);
          return;
        }

        data.forEach((product) => {
              const sizes = product.sizes || [];

              // calculate total rows for product rowspan
              let totalRows = 0;
              sizes.forEach((size) => {
                const prices = size.prices || [];
                if (prices.length === 0) {
                  totalRows += 1; // size with no prices
                } else {
                  prices.forEach((price) => {
                    totalRows += Math.max((price.dealers && price.dealers.length) || 1, 1);
                  });
                }
              });
              if (totalRows === 0) totalRows = 1; // product with no sizes

              let currentRowIndex = 0;
              let firstProductRow = true;

              if (sizes.length > 0) {
                sizes.forEach((size, sIndex) => {
                  const prices = size.prices || [];
                  let sizeRowsCount = 0;
                  
                  // Calculate rows for this size
                  if (prices.length === 0) {
                    sizeRowsCount = 1;
                  } else {
                    prices.forEach((price) => {
                      sizeRowsCount += Math.max((price.dealers && price.dealers.length) || 1, 1);
                    });
                  }

                  let firstSizeRow = true;

                  if (prices.length > 0) {
                    prices.forEach((price, pIndex) => {
                      const dealers = price.dealers || [];
                      const priceRowspan = Math.max(dealers.length, 1);

                      if (dealers.length > 0) {
                        dealers.forEach((dealer, dIndex) => {
                          const tr = document.createElement("tr");
                          tr.innerHTML = `
                            ${firstProductRow ? `<td rowspan="${totalRows}">${product.photo ? `<img src="${product.photo}" alt="Photo" width="50">` : ""}</td>` : ""}
                            ${firstProductRow ? `<td rowspan="${totalRows}">${product.name || ""}</td>` : ""}
                            ${firstSizeRow ? `<td rowspan="${sizeRowsCount}">${size.size || ""}</td>` : ""}
                            ${firstSizeRow ? `<td rowspan="${sizeRowsCount}">${size.code || ""}</td>` : ""}
                            ${firstSizeRow ? `<td rowspan="${sizeRowsCount}">${size.hsn || ""}</td>` : ""}
                            ${firstSizeRow ? `<td rowspan="${sizeRowsCount}">${size.mrp || ""}</td>` : ""}
                            ${dIndex === 0 ? `<td rowspan="${priceRowspan}">${price.payment_type || ""}</td>` : ""}
                            ${dIndex === 0 ? `<td rowspan="${priceRowspan}">${price.price || ""}</td>` : ""}
                            ${dIndex === 0 ? `<td rowspan="${priceRowspan}"><div>${price.discount || ""}%</div><small class="text-muted">₹${price.discount_price || ""}</small></td>` : ""}
                            ${dIndex === 0 ? `<td rowspan="${priceRowspan}"><div>${price.tax || ""}%</div><small class="text-muted">₹${price.tax_price || ""}</small></td>` : ""}
                            ${dIndex === 0 ? `<td rowspan="${priceRowspan}">${price.box || ""}</td>` : ""}
                            ${dIndex === 0 ? `<td rowspan="${priceRowspan}"><div>${price.box_discount || ""}%</div><small class="text-muted">₹${price.box_discount_price || ""}</small></td>` : ""}
                            ${dIndex === 0 ? `<td rowspan="${priceRowspan}"><div>${price.box_tax || ""}%</div><small class="text-muted">₹${price.box_tax_price || ""}</small></td>` : ""}
                            <td>${dealer?.dlr_name || ""}</td>
                            <td>${dealer?.slol || ""}</td>
                            <td>${dealer?.purchase_date || ""}</td>
                            <td>${dealer?.purchase_price || ""}</td>
                            <td><div>${dealer?.purchase_discount || ""}%</div><small class="text-muted">₹${dealer?.purchase_discount_price || ""}</small></td>
                            <td><div>${dealer?.purchase_tax || ""}%</div><small class="text-muted">₹${dealer?.purchase_tax_price || ""}</small></td>
                            <td>${dealer?.purchase_box || ""}</td>
                            <td><div>${dealer?.purchase_box_discount || ""}%</div><small class="text-muted">₹${dealer?.purchase_box_discount_price || ""}</small></td>
                            <td><div>${dealer?.purchase_box_tax || ""}%</div><small class="text-muted">₹${dealer?.purchase_box_tax_price || ""}</small></td>
                            ${firstProductRow ? `<td rowspan="${totalRows}">
                              <button class="btn btn-sm btn-success" onclick="editProduct(${product.id})" title="Edit Product">✎</button>
                              <button class="btn btn-sm btn-danger" onclick="deleteProduct(${product.id})" title="Delete Product">🗑</button>
                            </td>` : ""}
                          `;
                          tbody.appendChild(tr);
                          firstProductRow = false;
                          firstSizeRow = false;
                        });
                      } else {
                        // Price with no dealers
                        const tr = document.createElement("tr");
                        tr.innerHTML = `
                          ${firstProductRow ? `<td rowspan="${totalRows}">${product.photo ? `<img src="${product.photo}" alt="Photo" width="50">` : ""}</td>` : ""}
                          ${firstProductRow ? `<td rowspan="${totalRows}">${product.name || ""}</td>` : ""}
                          ${firstSizeRow ? `<td rowspan="${sizeRowsCount}">${size.size || ""}</td>` : ""}
                          ${firstSizeRow ? `<td rowspan="${sizeRowsCount}">${size.code || ""}</td>` : ""}
                          ${firstSizeRow ? `<td rowspan="${sizeRowsCount}">${size.hsn || ""}</td>` : ""}
                          ${firstSizeRow ? `<td rowspan="${sizeRowsCount}">${size.mrp || ""}</td>` : ""}
                          <td>${price.payment_type || ""}</td>
                          <td>${price.price || ""}</td>
                          <td><div>${price.discount || ""}%</div><small class="text-muted">₹${price.discount_price || ""}</small></td>
                          <td><div>${price.tax || ""}%</div><small class="text-muted">₹${price.tax_price || ""}</small></td>
                          <td>${price.box || ""}</td>
                          <td><div>${price.box_discount || ""}%</div><small class="text-muted">₹${price.box_discount_price || ""}</small></td>
                          <td><div>${price.box_tax || ""}%</div><small class="text-muted">₹${price.box_tax_price || ""}</small></td>
                          <td colspan="9">No dealers</td>
                          ${firstProductRow ? `<td rowspan="${totalRows}">
                            <button class="btn btn-sm btn-success" onclick="editProduct(${product.id})" title="Edit Product">✎</button>
                            <button class="btn btn-sm btn-danger" onclick="deleteProduct(${product.id})" title="Delete Product">🗑</button>
                          </td>` : ""}
                        `;
                        tbody.appendChild(tr);
                        firstProductRow = false;
                        firstSizeRow = false;
                      }
                    });
                  } else {
                    // Size with no prices
                    const tr = document.createElement("tr");
                    tr.innerHTML = `
                      ${firstProductRow ? `<td rowspan="${totalRows}">${product.photo ? `<img src="${product.photo}" alt="Photo" width="50">` : ""}</td>` : ""}
                      ${firstProductRow ? `<td rowspan="${totalRows}">${product.name || ""}</td>` : ""}
                      <td>${size.size || ""}</td>
                      <td>${size.code || ""}</td>
                      <td>${size.hsn || ""}</td>
                      <td>${size.mrp || ""}</td>
                      <td colspan="16">No prices defined</td>
                      ${firstProductRow ? `<td rowspan="${totalRows}">
                        <button class="btn btn-sm btn-success" onclick="editProduct(${product.id})" title="Edit Product">✎</button>
                        <button class="btn btn-sm btn-danger" onclick="deleteProduct(${product.id})" title="Delete Product">🗑</button>
                      </td>` : ""}
                    `;
                    tbody.appendChild(tr);
                    firstProductRow = false;
                  }
                });
              } else {
                // Product with no sizes
                const tr = document.createElement("tr");
                tr.innerHTML = `
                  <td>${product.photo ? `<img src="${product.photo}" alt="Photo" width="50">` : ""}</td>
                  <td>${product.name || ""}</td>
                  <td colspan="20">No sizes defined</td>
                  <td>
                    <button class="btn btn-sm btn-success" onclick="editProduct(${product.id})" title="Edit Product">✎</button>
                    <button class="btn btn-sm btn-danger" onclick="deleteProduct(${product.id})" title="Delete Product">🗑</button>
                  </td>
                `;
                tbody.appendChild(tr);
              }
            });
      }

      // --- Edit Product Function ---
      function editProduct(productId) {
        console.log(`🔧 Editing product ID: ${productId}`);
        
        // Fetch the specific product data
        fetch(`/api/product-create/`)
          .then(res => res.json())
          .then(products => {
            const product = products.find(p => p.id === productId);
            if (!product) {
              console.error('❌ Product not found!');
              return;
            }
            
            // Clear existing form and populate with product data
            populateFormWithProductData(product);
          })
          .catch(err => {
            console.error('❌ Error fetching product:', err);
          });
      }

      // --- Populate Form with Product Data ---
      function populateFormWithProductData(product) {
        // Clear existing form
        document.getElementById('productList').innerHTML = '';
        
        // Reset counters
        productCount = 0;
        sizeCount = 0;
        priceCount = 0;
        
        // Store the product ID for updating instead of creating new
        editingProductId = product.id;
        
        // Change UI to indicate edit mode
        document.getElementById("saveProductsBtn").textContent = "🔄 Update Product";
        document.getElementById("saveProductsBtn").className = "btn btn-warning mt-2 w-100";
        document.getElementById("saveProductsBtn").style.display = "block";
        document.getElementById("cancelEditBtn").style.display = "block";
        
        // Show a message to user that they're in edit mode
        console.log(`📝 Editing product: ${product.name} (ID: ${product.id})`);
        
        // Add product row first - this creates the basic structure
        addProductRow();
        
        // Fill in product basic info
        const productRow = document.getElementById('product_0');
        if (productRow) {
          const inputs = productRow.querySelectorAll('input');
          if (inputs.length >= 2) {
            // Show existing photo preview if available
            if (product.photo) {
              console.log(`📷 Current photo: ${product.photo}`);
              const photoCell = inputs[0].parentElement;
              const existingPreview = photoCell.querySelector('.existing-photo-preview');
              
              if (!existingPreview) {
                const previewDiv = document.createElement('div');
                previewDiv.className = 'existing-photo-preview mt-1';
                previewDiv.innerHTML = `
                  <div style="display: flex; align-items: center; gap: 8px; margin-top: 4px;">
                    <img src="${product.photo}" alt="Current Photo" style="width: 40px; height: 40px; object-fit: cover; border: 1px solid #ddd; border-radius: 4px; flex-shrink: 0;">
                    <div style="flex: 1; font-size: 12px;">
                      <div class="text-muted">Current photo</div>
                      <div class="text-info">Select new or keep current</div>
                    </div>
                    <button type="button" class="btn btn-sm btn-outline-danger" onclick="removeCurrentPhoto(this)" title="Remove current photo" style="padding: 2px 6px; font-size: 10px;">✕</button>
                  </div>
                `;
                photoCell.appendChild(previewDiv);
              }
            }
            inputs[1].value = product.name || '';   // Name input
          }
        }
        
        // Add sizes, prices, and dealers using existing functions
        if (product.sizes && product.sizes.length > 0) {
          product.sizes.forEach((size, sizeIndex) => {
            // Add size row using existing function - this increments sizeCount
            addSizeRow(0);
            
            // Get the actual sizeId that was just created (sizeCount - 1)
            const actualSizeId = sizeCount - 1;
            
            // Fill size data - find the size row by the actual generated ID
            const currentSizeRow = document.querySelector(`.product_0_size[data-size-id="${actualSizeId}"]`);
            
            if (currentSizeRow) {
              const sizeInputs = currentSizeRow.querySelectorAll('input');
              if (sizeInputs.length >= 4) {
                sizeInputs[0].value = size.size || '';
                sizeInputs[1].value = size.code || '';
                sizeInputs[2].value = size.hsn || '';
                sizeInputs[3].value = size.mrp || '';
              }
              
              // Add prices for this size
              if (size.prices && size.prices.length > 0) {
                size.prices.forEach((price, priceIndex) => {
                  // Add price row using existing function - this increments priceCount
                  addPriceRow(0, actualSizeId);
                  
                  // Get the actual priceId that was just created (priceCount - 1)
                  const actualPriceId = priceCount - 1;
                  
                  // Fill price data - find the price row by the actual generated ID
                  const currentPriceRow = document.querySelector(`.product_0_size_${actualSizeId}_price[data-price-id="${actualPriceId}"]`);
                  
                  if (currentPriceRow) {
                    // Payment type (select)
                    const paymentSelect = currentPriceRow.querySelector('select');
                    if (paymentSelect) paymentSelect.value = price.payment_type || 'cash';
                    
                    // Price inputs in order they appear in the HTML
                    const inputs = currentPriceRow.querySelectorAll('input');
                    let inputIndex = 0;
                    
                    if (inputs[inputIndex]) inputs[inputIndex].value = price.price || '';
                    inputIndex++;
                    if (inputs[inputIndex]) inputs[inputIndex].value = price.discount || '';
                    inputIndex++;
                    if (inputs[inputIndex]) inputs[inputIndex].value = price.discount_price || '';
                    inputIndex++;
                    if (inputs[inputIndex]) inputs[inputIndex].value = price.tax || '';
                    inputIndex++;
                    if (inputs[inputIndex]) inputs[inputIndex].value = price.tax_price || '';
                    inputIndex++;
                    if (inputs[inputIndex]) inputs[inputIndex].value = price.box || '';
                    inputIndex++;
                    if (inputs[inputIndex]) inputs[inputIndex].value = price.box_discount || '';
                    inputIndex++;
                    if (inputs[inputIndex]) inputs[inputIndex].value = price.box_discount_price || '';
                    inputIndex++;
                    if (inputs[inputIndex]) inputs[inputIndex].value = price.box_tax || '';
                    inputIndex++;
                    if (inputs[inputIndex]) inputs[inputIndex].value = price.box_tax_price || '';
                    
                    // Add dealers for this price
                    if (price.dealers && price.dealers.length > 0) {
                      price.dealers.forEach((dealer, dealerIndex) => {
                        // Add dealer row using existing function
                        addDealerRow(currentPriceRow, 0, actualSizeId, actualPriceId);
                        
                        // Fill dealer data - get all dealer rows for this price and select the most recent one
                        const dealerRows = document.querySelectorAll(`.product_0_size_${actualSizeId}_price_${actualPriceId}_dealer`);
                        const currentDealerRow = dealerRows[dealerRows.length - 1]; // Get the last added dealer row
                        
                        if (currentDealerRow) {
                          const dealerInputs = currentDealerRow.querySelectorAll('input');
                          let dealerInputIndex = 0;
                          
                          if (dealerInputs[dealerInputIndex]) dealerInputs[dealerInputIndex].value = dealer.dlr_name || '';
                          dealerInputIndex++;
                          if (dealerInputs[dealerInputIndex]) dealerInputs[dealerInputIndex].value = dealer.slol || '';
                          dealerInputIndex++;
                          if (dealerInputs[dealerInputIndex]) dealerInputs[dealerInputIndex].value = dealer.purchase_date || '';
                          dealerInputIndex++;
                          if (dealerInputs[dealerInputIndex]) dealerInputs[dealerInputIndex].value = dealer.purchase_price || '';
                          dealerInputIndex++;
                          if (dealerInputs[dealerInputIndex]) dealerInputs[dealerInputIndex].value = dealer.purchase_discount || '';
                          dealerInputIndex++;
                          if (dealerInputs[dealerInputIndex]) dealerInputs[dealerInputIndex].value = dealer.purchase_discount_price || '';
                          dealerInputIndex++;
                          if (dealerInputs[dealerInputIndex]) dealerInputs[dealerInputIndex].value = dealer.purchase_tax || '';
                          dealerInputIndex++;
                          if (dealerInputs[dealerInputIndex]) dealerInputs[dealerInputIndex].value = dealer.purchase_tax_price || '';
                          dealerInputIndex++;
                          if (dealerInputs[dealerInputIndex]) dealerInputs[dealerInputIndex].value = dealer.purchase_box || '';
                          dealerInputIndex++;
                          if (dealerInputs[dealerInputIndex]) dealerInputs[dealerInputIndex].value = dealer.purchase_box_discount || '';
                          dealerInputIndex++;
                          if (dealerInputs[dealerInputIndex]) dealerInputs[dealerInputIndex].value = dealer.purchase_box_discount_price || '';
                          dealerInputIndex++;
                          if (dealerInputs[dealerInputIndex]) dealerInputs[dealerInputIndex].value = dealer.purchase_box_tax || '';
                          dealerInputIndex++;
                          if (dealerInputs[dealerInputIndex]) dealerInputs[dealerInputIndex].value = dealer.purchase_box_tax_price || '';
                        }
                      });
                    }
                  }
                });
              }
            }
          });
        }
        
        console.log('✅ Product loaded into form for editing');
        
        // Scroll to top of form so user can see the loaded data
        document.getElementById('productTable').scrollIntoView({ behavior: 'smooth' });
      }

      // Call the correct function when page loads
      window.addEventListener("DOMContentLoaded", () => {
        displayProductsWithNestedStructure();
      });
      
