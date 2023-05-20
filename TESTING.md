# Testing

## Contents

- [Manual Testing](#manual-testing)
- [Automated Testing](#automated-testing)
- [User Stories Testing](#user-stories-testing)
- [Validator Testing](#validator-testing)
  - [HTML](#html)
  - [CSS](#css)
  - [JS](#js)
  - [Python](#python)
- [Performance Testing](#performance-testing)
  - [Desktop Results](#desktop-results)
  - [Mobile Results](#mobile-results)
- [Browser Compatibility](#browser-compatibility)
- [Responsivity](#responsivity)
- [Issues/ Bugs Found & Resolved](#issues-bugs)
- [Unresolved](#unresolved)

---
Back to the [README](README.md)<br>

## <a name="manual-testing">Manual Testing</a>

## <a name="automated-testing">Automated Testing</a>

Python **Automated Unit Testing** was implemented using the [Django Unit Testing](https://docs.djangoproject.com/en/3.2/topics/testing/overview/) framework.  
**Unit Tests** have been written to cover all major parts of the code like **Forms**, **Models**, **Views**, **Admin**, **Context-Processors** and **Fields**. The tests were created to cover all key aspects of the code. Only the checkout app has a moderate coverage, but here manual testing was applied.
A total of **228** **Unit Tests** have been written. All **228** tests ran successfully without errors or warnings.   

<details>
    <summary>Coverage Automated Testing</summary>
    <img src="documentation/testing/automated-testing/coverage.png">
    <img src="documentation/testing/automated-testing/coverage-report1.png">
    <img src="documentation/testing/automated-testing/coverage-report2.png">
</details>

<br>

## <a name="user-stories-testing">User Stories Testing</a>

## <a name="validator-testing">Validator Testing</a>

### <a name="html">HTML</a>
All **HTML** code was validated using the [W3C Markup Validation Service](https://validator.w3.org/) regularly during the development process. **The HTML Source Code** was regularly viewed for each page using **Google Chrome** and passed through the [W3C Markup Validation Service](https://validator.w3.org/). Various minor errors were encountered and corrected during the final **HTML** validation check.

A slightly tricky error was the error to the auto-focus. For login/signup I created a modal that loads on all pages. This modal has two tabs: one tab for login and one tab for signup. Accordingly, two forms load in one modal and Crispy Froms automatically sets an auto-focus for each form. Thus I had more than one auto-focus on the page. I could have manipulated the DOM to enable auto-focus for only the from that is open and disable it otherwise. However, the form would still have been rendered with auto-focus and the test would have returned an error. In the tutoring support we came up with the idea to create a context processor that handles the tags for signup and login. For this I have created a `CustomLoginForm` which disables the auto-focus. The context processor will then load the corresponding `CustomLoginForm` in the `logintag`

A slightly unpleasant error was the duplicate of the `div_id_email` that occurred in the checkout. Crispy Forms creates a wrapper DIV around the input element and assigns the DIV ID `div_id_email` for email. Since I have two forms on the page with email, one being the `OrderForm` and the other being the `login/signup modal`, there was a conflict here. I haven't found a really convinient solution to control the ID of the wrapper DIV with the existing OrderForm setup. One solution would have been to create the OrderForm entirely new with the `Crispy Form Helpers and Layout`. This would have given me the possibility to give the wrapper DIV its own ID. The other option would have been to manually create this input field in the HTML code. This was the solution I chose, as it was less invasive. Later on, I found the proper solution in the Django documentation. With the paramater `auto_id` I was able to control the Id of the wrapper DIV. I reversed the changes from before and the email field is rendered normally again and the DIV ID is now unique for the Login and SIngup fields. 

### Errors during validation check

<details>
    <summary>Home Page</summary>
    <img src="documentation/testing/validator/html/validator-error-w3-homepage.png">
</details>
<details>
    <summary>CLP</summary>
    <img src="documentation/testing/validator/html/validator-error-w3-clp.png">
</details>
<details>
    <summary>Shopping Bag</summary>
    <img src="documentation/testing/validator/html/validator-error-w3-bag-1.png">
    <img src="documentation/testing/validator/html/validator-error-w3-bag-2.png">
</details>
<details>
    <summary>Checkout</summary>
    <img src="documentation/testing/validator/html/validator-error-w3-checkout.png">
</details>
<details>
    <summary>Profile</summary>
    <img src="documentation/testing/validator/html/validator-error-w3-profile-1.png">
    <img src="documentation/testing/validator/html/validator-error-w3-profile-2.png">
</details>


### Results validation check


### <a name="css">CSS</a>

**Custom CSS Styling** from [admin.css](admin/static/admin/css/admin.css), [base.css](static/css/base.css), [bag.css](bag/static/bag/css/bag.css), 
[checkout.css](checkout/static/checkout/css/checkout.css), [products.css](products/static/products/css/products.css), [profiles.css](profiles/static/profiles/css/profiles.css) and [support.css](support/static/support/css/support.css).
was validated using the [W3C CSS Validation Service](https://jigsaw.w3.org/css-validator/).  
No errors were generated.

### Results

<details>
    <summary>Base.css</summary>
</details>
<details>
    <summary>Admin.css</summary>
</details>
<details>
    <summary>Bag.css</summary>
</details>
<details>
    <summary>Checkout.css</summary>
</details>
<details>
    <summary>Products.css</summary>
</details>
<details>
    <summary>Profiles.css</summary>
</details>
<details>
    <summary>Support.css</summary>
</details>

### <a name="js">JavaScript</a>

The custom scripts, were validated using the [JSHint](https://jshint.com/about/) static code analysis tool. Due to the lack of complexity of **JavaScript** code implemented on the project, **Automated Unit Testing** of the **JavaScript** code was considered unnecessary. All **JavaScript** functions and event handlers in the custom **JavaScript Code Libraries** have been thoroughly manually debugged and tested in the console.

In checkout a warning was displayed that the variable Stripe is undefined. However, this is defined by the Stripe JS and therefore this message was not pursued further.

### Results

<details>
    <summary>Bag</summary>
    <img src="documentation/testing/validator/js/update_remove_qty_from_bag.png">
</details>
<details>
    <summary>Checkout</summary>
    <img src="documentation/testing/validator/js/stripe_elements.png">
</details>
<details>
    <summary>Products</summary>
    <img src="documentation/testing/validator/js/add_product_to_bag.png">
    <img src="documentation/testing/validator/js/add_to_wishlist.png">
    <img src="documentation/testing/validator/js/filters.png">
    <img src="documentation/testing/validator/js/quantity_input.png">
</details>
<details>
    <summary>Profiles</summary>
    <img src="documentation/testing/validator/js/countryfield.png">
    <img src="documentation/testing/validator/js/profile_btn_toggle.png">
    <img src="documentation/testing/validator/js/star_rating.png">
</details>
<br>


### <a name="Python">Python</a>

## <a name="performance-testing">Performance Testing</a>

### <a name="desktop-results">Desktop Results</a>
### <a name="mobile-results">Mobile Results</a>

## <a name="browser-compatibility">Browser Compatibility</a>

## <a name="responsivity">Responsivity</a>

## <a name="issues-bugs">Issues/ Bugs Found & Resolved</a>