Feature: As a user, I can create and publish new pages

  Scenario: Create my first web page after login
    Given anonymous user on the admin page
    Then I see the login page
    When I fill the field "username" with "alice"
    And I fill the field "password" with "secret"
    And I click on the "Sign In" button
    Then I see the text "Create my first page"
    When I click on the "Create my first page" link
    Then I see the text "Available Templates"
    And I see the text "blog:HomePage"

  Scenario: Create new page
    Given user on the admin page
    When I click on the "Create my first page" link
    And I click on the "blog:HomePage" link
    And I fill the field "slug" with "/"
    And I fill the field "title" with "welcome home"
    And I fill the field "description" with "there is not place like home"

    And I click on the "Add Item" button
    And I fill the "second" field "title" with "Intro"
    And I fill the textarea field "body" with "<p>Welcome aboard!</p>"

    And I click on the "Add Item" button
    And I fill the "third" field "title" with "Outro"
    And I fill the "second" textarea field "body" with "<p>Rich text widget not implemented yet</p>"

    And I click on the "Submit" button
    And I visit "/"
    And I wait
    Then I see the text "welcome home"
