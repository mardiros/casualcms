Feature: As a user, I can create and publish new pages

  Scenario: Create my first web page after login
    Given anonymous user on the admin page
    Then I see the login page
    When I fill the field "username" with "alice"
    And I fill the field "password" with "secret"
    And I click on the "Sign In" button
    Then I see the text "Create my first page"
    When I click on the "Create my first page" link
    Then I see the text "Choose A Type Of Page"
    And I see the text "Home Page"

  Scenario: Create new page
    Given user on the admin page
    When I click on the "Create my first page" link
    And I click on the "Home Page" link
    And I fill the field "slug" with "home"
    And I fill the field "title" with "welcome home"
    And I fill the field "hero_title" with "welcome home"
    And I fill the field "description" with "there is not place like home"
    # First paragraph
    And I click on the "Add Item" button
    And I fill the "second" field "title" with "Intro"
    And I fill the richtext field "body" with "Welcome aboard!"
    # Second paragraph
    And I click on the "Add Item" button
    And I fill the "third" field "title" with "Outro"
    And I fill the "second" richtext field "body" with "Rich text widget !"
    And I click on the "Create Page" button
    # List pages
    Then I see the text "welcome home"
    And I see the text "Edit"
    # Check the preview
    When I click on the "Preview" link ignoring the target attribute
    Then I see the text "welcome home"
    And I see the text "Welcome aboard!"
