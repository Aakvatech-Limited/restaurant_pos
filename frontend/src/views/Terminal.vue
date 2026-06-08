<template>
  <div class="h-full flex overflow-hidden">
    <!-- Left Panel: Menu & Navigation -->
    <div class="flex-1 flex flex-col p-6 overflow-hidden bg-[#0c0c16]">
      <!-- Quick Options & Order Type Selection -->
      <div class="flex justify-between items-center mb-6 shrink-0">
        <div class="flex bg-white/5 p-1 rounded-2xl border border-white/5">
          <button 
            v-for="type in ['Dine-In', 'Take-Away', 'Delivery']" 
            :key="type"
            @click="orderType = type"
            :class="['px-5 py-2.5 rounded-xl text-sm font-semibold transition', orderType === type ? 'bg-indigo-600 text-white shadow-lg' : 'text-slate-400 hover:text-white']"
          >
            {{ type }}
          </button>
        </div>

        <!-- Search Bar -->
        <div class="relative w-80">
          <span class="absolute inset-y-0 left-0 pl-3.5 flex items-center text-slate-400">
            <i class="fa-solid fa-magnifying-glass"></i>
          </span>
          <input 
            v-model="searchQuery" 
            type="text" 
            placeholder="Search item name or code..." 
            class="w-full pl-10 pr-4 py-3 rounded-2xl bg-white/5 border border-white/5 focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500 text-sm placeholder-slate-500"
          >
        </div>
      </div>

      <!-- Dine-In: Table Management Grid -->
      <div v-if="orderType === 'Dine-In'" class="mb-6 bg-[#121224] p-4 rounded-3xl border border-white/5 shrink-0">
        <h3 class="text-xs font-bold text-slate-400 uppercase tracking-widest mb-3">Select Active Table</h3>
        <div class="grid grid-cols-6 gap-3">
          <button 
            v-for="table in tables" 
            :key="table.id"
            @click="selectedTable = table.id"
            :class="[
              'p-3.5 rounded-2xl border text-center transition duration-300',
              selectedTable === table.id 
                ? 'bg-indigo-600 border-indigo-500 text-white scale-105 shadow-lg shadow-indigo-600/20' 
                : 'bg-white/5 border-white/5 text-slate-300 hover:bg-white/10'
            ]"
          >
            <div class="font-bold text-sm">{{ table.name }}</div>
            <div class="text-[10px] opacity-65 mt-1">{{ table.status }}</div>
          </button>
        </div>
      </div>

      <!-- Item Groups / Categories Slider -->
      <div class="flex gap-2.5 overflow-x-auto pb-3 mb-4 shrink-0 no-scrollbar">
        <button 
          @click="selectedCategory = ''"
          :class="['px-5 py-2.5 rounded-2xl text-xs font-bold uppercase tracking-wider shrink-0 transition', !selectedCategory ? 'bg-indigo-600 text-white shadow-lg' : 'bg-white/5 text-slate-400 hover:text-white']"
        >
          All Menu
        </button>
        <button 
          v-for="category in categories" 
          :key="category"
          @click="selectedCategory = category"
          :class="['px-5 py-2.5 rounded-2xl text-xs font-bold uppercase tracking-wider shrink-0 transition', selectedCategory === category ? 'bg-indigo-600 text-white shadow-lg' : 'bg-white/5 text-slate-400 hover:text-white']"
        >
          {{ category }}
        </button>
      </div>

      <!-- Menu Items Grid -->
      <div class="flex-1 overflow-y-auto pr-1">
        <div class="grid grid-cols-4 gap-4">
          <div 
            v-for="item in filteredItems" 
            :key="item.name"
            @click="addToCart(item)"
            class="bg-[#121224] rounded-3xl p-4 border border-white/5 hover:border-white/10 hover:-translate-y-1 transition duration-300 cursor-pointer flex flex-col justify-between group"
          >
            <div class="relative rounded-2xl overflow-hidden mb-3 aspect-video bg-white/5">
              <img 
                :src="item.image || 'https://images.unsplash.com/photo-1546069901-ba9599a7e63c?auto=format&fit=crop&q=80&w=300'" 
                class="w-full h-full object-cover group-hover:scale-105 transition duration-500" 
                alt="item.item_name"
              >
              <span class="absolute top-2 right-2 bg-black/60 backdrop-blur-md text-indigo-400 px-2.5 py-1 rounded-xl text-xs font-bold">
                {{ item.item_group }}
              </span>
            </div>
            <div>
              <h4 class="font-bold text-slate-200 group-hover:text-indigo-400 transition truncate">{{ item.item_name }}</h4>
              <p class="text-xs text-slate-500 line-clamp-2 mt-1 mb-3">{{ item.description || 'Delectable chef special cooked to perfection.' }}</p>
              <div class="flex justify-between items-center">
                <span class="text-lg font-extrabold text-white">${{ parseFloat(item.standard_rate || 0).toFixed(2) }}</span>
                <span class="w-8 h-8 rounded-xl bg-indigo-600/10 text-indigo-400 flex items-center justify-center text-xs group-hover:bg-indigo-600 group-hover:text-white transition duration-300">
                  <i class="fa-solid fa-plus"></i>
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Right Panel: Order Cart Sidebar -->
    <div class="w-[420px] bg-[#121224] border-l border-white/5 flex flex-col p-6 shadow-2xl shrink-0">
      <div class="flex justify-between items-center mb-6 shrink-0">
        <h2 class="text-xl font-bold text-white flex items-center gap-2">
          <i class="fa-solid fa-receipt text-indigo-500"></i> Active Cart
        </h2>
        <button @click="clearCart" class="text-xs text-rose-400 hover:text-rose-300 font-medium">Clear All</button>
      </div>

      <!-- Cart Item List -->
      <div class="flex-1 overflow-y-auto space-y-4 pr-1">
        <div v-if="!cart.length" class="text-center py-24 text-slate-500 flex flex-col items-center">
          <i class="fa-solid fa-utensils text-5xl mb-4 text-slate-700"></i>
          <p class="font-medium text-sm">Select items to start ordering</p>
        </div>
        
        <div v-for="(cartItem, idx) in cart" :key="idx" class="bg-white/5 p-4 rounded-2xl border border-white/5 space-y-3">
          <div class="flex justify-between items-start">
            <div class="min-w-0 flex-1 pr-2">
              <input 
                v-model="cartItem.print_name" 
                class="font-bold text-slate-200 bg-transparent focus:outline-none border-b border-transparent focus:border-slate-500 w-full text-sm"
                placeholder="Item Print Name"
              >
              <div class="text-[10px] text-indigo-400 font-semibold mt-0.5">{{ cartItem.item_code }}</div>
            </div>
            <div class="text-right">
              <span class="text-sm font-extrabold text-white">${{ (cartItem.standard_rate * cartItem.qty).toFixed(2) }}</span>
            </div>
          </div>

          <!-- Modifiers & Extra Ingredients -->
          <div class="flex flex-wrap gap-1.5 pt-1">
            <span v-for="mod in cartItem.modifiers" :key="mod.item_code" class="text-[10px] bg-indigo-950/60 border border-indigo-500/20 text-indigo-300 px-2 py-0.5 rounded-lg">
              + {{ mod.item_name }} (+${{ mod.rate }})
            </span>
            <button @click="openModifiersModal(idx)" class="text-[10px] text-indigo-400 hover:underline flex items-center gap-1 font-semibold">
              <i class="fa-solid fa-plus-circle"></i> Add Modifiers
            </button>
          </div>

          <!-- Per-item Remark Input -->
          <div class="relative">
            <input 
              v-model="cartItem.remarks" 
              type="text" 
              placeholder="Remark / Chef instructions..." 
              class="w-full bg-white/5 border border-white/5 rounded-xl px-3 py-1.5 text-xs focus:outline-none text-slate-300"
            >
          </div>

          <!-- Quantity adjustments -->
          <div class="flex justify-between items-center pt-2 border-t border-white/5">
            <button @click="removeFromCart(idx)" class="text-xs text-rose-400 hover:underline">Remove</button>
            <div class="flex items-center gap-3">
              <button @click="updateQty(idx, -1)" class="w-7 h-7 rounded-xl bg-white/5 hover:bg-white/10 flex items-center justify-center text-xs"><i class="fa-solid fa-minus"></i></button>
              <span class="text-sm font-bold text-white">{{ cartItem.qty }}</span>
              <button @click="updateQty(idx, 1)" class="w-7 h-7 rounded-xl bg-white/5 hover:bg-white/10 flex items-center justify-center text-xs"><i class="fa-solid fa-plus"></i></button>
            </div>
          </div>
        </div>
      </div>

      <!-- Checkout Summary Panel -->
      <div v-if="cart.length" class="border-t border-white/5 pt-4 mt-4 space-y-4 shrink-0">
        <div class="space-y-2 text-xs">
          <div class="flex justify-between text-slate-400">
            <span>Subtotal:</span>
            <span class="font-medium text-slate-200">${{ cartTotal.toFixed(2) }}</span>
          </div>
          <div class="flex justify-between text-slate-400">
            <span>Discount (5%):</span>
            <span class="font-medium text-rose-400">-${{ cartDiscount.toFixed(2) }}</span>
          </div>
          <div class="flex justify-between text-lg font-extrabold text-white pt-2 border-t border-white/5">
            <span>Grand Total:</span>
            <span class="text-indigo-400">${{ grandTotal.toFixed(2) }}</span>
          </div>
        </div>

        <div class="grid grid-cols-2 gap-2">
          <button @click="printKOT" class="bg-indigo-950 text-indigo-400 border border-indigo-500/20 py-3 rounded-2xl font-bold text-xs flex items-center justify-center gap-2 hover:bg-indigo-900 transition">
            <i class="fa-solid fa-utensils"></i> Print KOT
          </button>
          <button @click="showCheckoutModal = true" class="bg-indigo-600 text-white py-3 rounded-2xl font-bold text-xs flex items-center justify-center gap-2 hover:bg-indigo-500 transition accent-glow">
            <i class="fa-solid fa-circle-check"></i> Place DN Order
          </button>
        </div>
      </div>
    </div>

    <!-- Modifiers Popup Modal -->
    <div v-if="showModifiersModal" class="fixed inset-0 z-50 flex items-center justify-center p-4">
      <div class="absolute inset-0 bg-black/70 backdrop-blur-sm" @click="showModifiersModal = false"></div>
      <div class="relative bg-[#121224] border border-white/10 w-full max-w-md rounded-3xl p-6 shadow-2xl">
        <div class="flex justify-between items-center mb-4">
          <h3 class="text-lg font-bold text-white">Add Modifiers/Sides</h3>
          <button @click="showModifiersModal = false" class="text-slate-400 hover:text-white"><i class="fa-solid fa-xmark"></i></button>
        </div>
        <div class="space-y-2 max-h-60 overflow-y-auto">
          <div 
            v-for="mod in availableModifiers" 
            :key="mod.item_code"
            @click="toggleModifier(mod)"
            :class="['p-3 rounded-xl border cursor-pointer flex justify-between items-center transition', hasModifier(mod) ? 'bg-indigo-600/10 border-indigo-500 text-indigo-300' : 'bg-white/5 border-white/5 text-slate-300']"
          >
            <span class="font-bold text-sm">{{ mod.item_name }}</span>
            <span class="font-bold text-xs text-indigo-400">+${{ mod.rate }}</span>
          </div>
        </div>
        <button @click="showModifiersModal = false" class="w-full bg-indigo-600 text-white py-3 rounded-2xl font-bold text-xs mt-4 hover:bg-indigo-500 transition">Apply Modifiers</button>
      </div>
    </div>

    <!-- Checkout / Customer Creation Modal -->
    <div v-if="showCheckoutModal" class="fixed inset-0 z-50 flex items-center justify-center p-4">
      <div class="absolute inset-0 bg-black/70 backdrop-blur-sm" @click="showCheckoutModal = false"></div>
      <div class="relative bg-[#121224] border border-white/10 w-full max-w-lg rounded-3xl p-6 shadow-2xl">
        <div class="flex justify-between items-center mb-6">
          <h3 class="text-xl font-bold text-white">Final Checkout (Stock Deduction)</h3>
          <button @click="showCheckoutModal = false" class="text-slate-400 hover:text-white"><i class="fa-solid fa-xmark"></i></button>
        </div>

        <!-- Customer Form -->
        <div class="space-y-4">
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-xs font-bold text-slate-400 mb-2 uppercase tracking-wide">Customer Name</label>
              <input v-model="customer.name" type="text" placeholder="John Doe" class="w-full bg-white/5 border border-white/5 rounded-2xl p-3 text-sm focus:outline-none text-white focus:ring-1 focus:ring-indigo-500">
            </div>
            <div>
              <label class="block text-xs font-bold text-slate-400 mb-2 uppercase tracking-wide">TIN Number (Tax ID)</label>
              <input v-model="customer.tin" type="text" placeholder="TIN-987654" class="w-full bg-white/5 border border-white/5 rounded-2xl p-3 text-sm focus:outline-none text-white focus:ring-1 focus:ring-indigo-500">
            </div>
          </div>
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-xs font-bold text-slate-400 mb-2 uppercase tracking-wide">WhatsApp Phone</label>
              <input v-model="customer.phone" type="text" placeholder="+123456789" class="w-full bg-white/5 border border-white/5 rounded-2xl p-3 text-sm focus:outline-none text-white focus:ring-1 focus:ring-indigo-500">
            </div>
            <div>
              <label class="block text-xs font-bold text-slate-400 mb-2 uppercase tracking-wide">Email Address</label>
              <input v-model="customer.email" type="email" placeholder="john@doe.com" class="w-full bg-white/5 border border-white/5 rounded-2xl p-3 text-sm focus:outline-none text-white focus:ring-1 focus:ring-indigo-500">
            </div>
          </div>

          <div v-if="orderType === 'Delivery'">
            <label class="block text-xs font-bold text-slate-400 mb-2 uppercase tracking-wide">Delivery Address & Instructions</label>
            <textarea v-model="deliveryAddress" placeholder="Street name, suite, city..." class="w-full bg-white/5 border border-white/5 rounded-2xl p-3 text-sm focus:outline-none text-white focus:ring-1 focus:ring-indigo-500 h-20"></textarea>
          </div>

          <!-- Send Settings -->
          <div class="flex gap-4 items-center bg-white/5 p-4 rounded-2xl border border-white/5">
            <label class="flex items-center gap-2 text-xs font-semibold text-slate-300 cursor-pointer">
              <input v-model="sendWhatsApp" type="checkbox" class="accent-indigo-500 w-4 h-4 rounded"> Send WhatsApp Invoice
            </label>
            <label class="flex items-center gap-2 text-xs font-semibold text-slate-300 cursor-pointer">
              <input v-model="sendEmail" type="checkbox" class="accent-indigo-500 w-4 h-4 rounded"> Send Email Invoice
            </label>
          </div>
        </div>

        <div class="flex gap-3 mt-6">
          <button @click="showCheckoutModal = false" class="flex-1 bg-white/5 text-slate-300 py-3.5 rounded-2xl font-bold text-sm hover:bg-white/10 transition">Cancel</button>
          <button 
            @click="submitCheckout" 
            :disabled="processingCheckout"
            class="flex-1 bg-indigo-600 text-white py-3.5 rounded-2xl font-bold text-sm hover:bg-indigo-500 transition accent-glow flex items-center justify-center gap-2"
          >
            <i v-if="processingCheckout" class="fa-solid fa-spinner animate-spin"></i>
            {{ processingCheckout ? 'Syncing...' : 'Submit Order' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'

const orderType = ref('Dine-In')
const selectedTable = ref('')
const searchQuery = ref('')
const selectedCategory = ref('')
const showModifiersModal = ref(false)
const showCheckoutModal = ref(false)
const processingCheckout = ref(false)
const selectedCartItemIndex = ref(null)

// Custom data mapping and local settings state
const items = ref([])
const categories = ref([])
const cart = ref([])
const tables = ref([
  { id: 'T1', name: 'Table 1', status: 'Available' },
  { id: 'T2', name: 'Table 2', status: 'Occupied' },
  { id: 'T3', name: 'Table 3', status: 'Dirty' },
  { id: 'T4', name: 'Table 4', status: 'Available' },
  { id: 'T5', name: 'Table 5', status: 'Billing' },
  { id: 'T6', name: 'Table 6', status: 'Available' },
])

const availableModifiers = ref([
  { item_code: 'MOD-CHSE', item_name: 'Extra Cheese', rate: 1.50, qty: 1 },
  { item_code: 'MOD-ONON', item_name: 'Caramelized Onions', rate: 1.00, qty: 1 },
  { item_code: 'MOD-BACN', item_name: 'Smoked Bacon strips', rate: 2.50, qty: 1 },
  { item_code: 'MOD-CHKN', item_name: 'Grilled Chicken extra', rate: 3.50, qty: 1 },
])

const customer = ref({ name: 'Cash Customer', tin: '', phone: '', email: '' })
const deliveryAddress = ref('')
const sendWhatsApp = ref(true)
const sendEmail = ref(false)

const cartTotal = computed(() => {
  return cart.value.reduce((acc, curr) => {
    const modsCost = curr.modifiers ? curr.modifiers.reduce((macc, mcurr) => macc + mcurr.rate, 0) : 0
    return acc + ((curr.standard_rate + modsCost) * curr.qty)
  }, 0)
})
const cartDiscount = computed(() => cartTotal.value * 0.05)
const grandTotal = computed(() => cartTotal.value - cartDiscount.value)

const filteredItems = computed(() => {
  return items.value.filter(item => {
    const matchCat = !selectedCategory.value || item.item_group === selectedCategory.value
    const matchSearch = !searchQuery.value || item.item_name.toLowerCase().includes(searchQuery.value.toLowerCase()) || item.name.toLowerCase().includes(searchQuery.value.toLowerCase())
    return matchCat && matchSearch
  })
})

const fetchItems = async () => {
  try {
    const res = await fetch('/api/method/restaurant_pos.api.get_items_by_group')
    const data = await res.json()
    items.value = data.message || [
      // Fallback mock items
      { name: 'ITEM-001', item_name: 'Cheeseburger Delight', item_group: 'Food', standard_rate: 8.50, image: '', description: 'Beef patty, double cheddar cheese, secret burger sauce.' },
      { name: 'ITEM-002', item_name: 'Tender Strips', item_group: 'Food', standard_rate: 6.99, image: '', description: 'Crispy hand-breaded chicken strips with choice of sauce.' },
      { name: 'ITEM-003', item_name: 'Old Fashioned Peg (30ml)', item_code: 'PEG-OLD-FASH', item_group: 'Alcohol', standard_rate: 12.00, image: '', description: 'Peg of bourbon with custom angostura and simple syrup.' },
      { name: 'ITEM-004', item_name: 'Tequila Sunrise Marg', item_group: 'Drinks', standard_rate: 9.50, image: '', description: 'Silver tequila, triple sec, lime juice.' }
    ]
    categories.value = [...new Set(items.value.map(i => i.item_group))]
  } catch (e) {
    console.error(e)
  }
}

const addToCart = (item) => {
  const existing = cart.value.find(c => c.item_code === item.name)
  if (existing) {
    existing.qty += 1
  } else {
    cart.value.push({
      item_code: item.name,
      item_name: item.item_name,
      print_name: item.item_name,
      standard_rate: item.standard_rate,
      qty: 1,
      remarks: '',
      modifiers: []
    })
  }
}

const updateQty = (idx, amount) => {
  cart.value[idx].qty += amount
  if (cart.value[idx].qty <= 0) {
    cart.value.splice(idx, 1)
  }
}

const removeFromCart = (idx) => {
  cart.value.splice(idx, 1)
}

const clearCart = () => {
  cart.value = []
}

// Modifiers Logic
const openModifiersModal = (idx) => {
  selectedCartItemIndex.value = idx
  showModifiersModal.value = true
}

const toggleModifier = (mod) => {
  const item = cart.value[selectedCartItemIndex.value]
  const existIdx = item.modifiers.findIndex(m => m.item_code === mod.item_code)
  if (existIdx > -1) {
    item.modifiers.splice(existIdx, 1)
  } else {
    item.modifiers.push({ ...mod })
  }
}

const hasModifier = (mod) => {
  if (selectedCartItemIndex.value === null) return false
  const item = cart.value[selectedCartItemIndex.value]
  return item.modifiers.some(m => m.item_code === mod.item_code)
}

const printKOT = () => {
  alert("Routing Food order to KOT printer and Drinks/Alcohol to BOT (Bar) printer!")
}

const submitCheckout = async () => {
  processingCheckout.value = true
  try {
    const res = await fetch('/api/method/restaurant_pos.api.process_pos_checkout', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        items: cart.value,
        customer_name: customer.value.name,
        order_type: orderType.value,
        phone: sendWhatsApp.value ? customer.value.phone : null,
        tin_number: customer.value.tin,
        table_id: orderType.value === 'Dine-In' ? selectedTable.value : null,
        remarks: orderType.value === 'Delivery' ? deliveryAddress.value : null
      })
    })
    
    if (res.ok) {
      alert("Order checked out successfully! Delivery Note created and stock reduced.")
      clearCart()
      showCheckoutModal.value = false
    } else {
      const err = await res.json()
      alert("Failed checkout: " + (err.exception || 'Stock/repaking validation failed.'))
    }
  } catch (e) {
    alert("Connection Error to ERPNext backend.")
  } finally {
    processingCheckout.value = false
  }
}

onMounted(() => {
  fetchItems()
})
</script>

<style scoped>
.no-scrollbar::-webkit-scrollbar {
  display: none;
}
.no-scrollbar {
  -ms-overflow-style: none;
  scrollbar-width: none;
}
</style>
