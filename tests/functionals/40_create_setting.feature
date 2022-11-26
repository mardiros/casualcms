Feature: As a user, I can create a site

  Scenario: Navigate to the new setting form
    Given user on the admin page
    And a "/home" draft page of type "blog:HomePage"
    And a "127.0.0.1:6556" site with "/home" root page
    And a "localhost" site with "/home" root page
    When I click on the "Settings" link
    Then I see the text "127.0.0.1:6556"
    And I see the text "localhost"
    When I click on the "first" link "Edit Settings"
    Then I see the text "Contact Setting"
    And I see the text "Feature Flag"
    When I click on the "Contact Setting" link
    Then I see the text "New Setting"

  Scenario: Create a Setting
    Given user on the admin page
    And a "/home" draft page of type "blog:HomePage"
    And a "127.0.0.1:6556" site with "/home" root page
    And a "localhost" site with "/home" root page
    When I visit "/admin/settings/localhost/contact/new"
    Then I see the text "New Setting"
    When I fill the field "email" with "bob@alice.net"
    And I click on the "Create Setting" button
    When I click on the "Contact Setting" link
    Then I see the text "Edit Setting"
    And the setting "contact" on "localhost" contains
      | email         |
      | bob@alice.net |

  Scenario: Create a Setting
    Given user on the admin page
    And a "/home" draft page of type "blog:HomePage"
    And a "127.0.0.1:6556" site with "/home" root page
    And a "localhost" site with "/home" root page
    And a "contact" setting on site "localhost"
    When I visit "/admin/settings/localhost/contact/edit"
    Then I see the text "Edit Setting"
    And I see the input "email" contains "alice@alice.net"
    When I fill the field "email" with "bob@alice.net"
    And I click on the "Save" button
    Then I see the text "Setting Type"
    And the setting "contact" on "localhost" contains
      | email         |
      | bob@alice.net |
